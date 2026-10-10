# Tutorial — EdgeStream-GW project walkthrough (Helveticore OÜ)

_Date: 24 September 2026_

This document explains, step by step, **how I proceeded** to build the Helveticore portfolio
and then implement the EdgeStream-GW module, and summarizes **all the code written** so far.

---

## Part 1 — The approach (how I proceeded)

### 1. Document discovery

I read the two source documents provided in the directory:

- `Helveticore projects strategic portfolio.docx` — the portfolio strategy (the
  "Strategic Triptych 2026-2027": 3 projects).
- `EdgeStream-GW SYSTEM AND SOFTWARE DESIGN DESCRIPTION.docx` — the high-level spec
  (SDD IEEE 1016) of the Edge Stream Gateway.

From these I extracted:

- The **3 projects**: EdgeStream-GW (IoT gateway), Fog-Crypto Core (FPGA accelerator),
  NetSentry-IoT (cybersecurity probe).
- The required **methodology**: CMMI Level 3 "Defined", expressed as **V-Model** (macro),
  **TDD** (micro) and **CBSE** (integration).
- The **architecture** of EdgeStream-GW: the pipeline `South Drivers → Protocol Adapters →
  Edge Analytics → Ingestion Core → Northbound Publishers`, plus `Local Action Engine`,
  `Store-and-Forward` and `Deployment`.

### 2. CMMI scaffolding (repository structure)

I created the following structure, shared by all projects:

```text
.
├── docs/        source documents (portfolio, SDD, company register)
├── process/     shared CMMI framework (charter + templates)
└── projects/
    ├── edgestream-gw/    (requirements, design, testbench, performance, src)
    ├── fog-crypto-core/
    └── netsentry-iot/
```

Each project has the same CMMI artifacts: `requirements/` (REQ + RTM), `design/` (SDD +
decision log), `testbench/`, `performance/`, `src/` (technical sub-projects).

### 3. English translation + PDF conversion

- All READMEs and documents were translated **to English**.
- The source `.docx` (SDD + portfolio) were converted **to PDF** (via LibreOffice headless).

### 4. Git versioning + GitHub push

- `git init` on the `main` branch, first commit, then `git remote` to
  `helvetou/EdgeStreamGW` (private repo).
- Every following step was **committed then pushed** to `main`.

### 5. Specification phase (easiest module)

I picked the simplest module that is also the most strategic: **Protocol Adapters**
(EdgeStream-GW), because it is:

- pure Python (`bytes → Frame`), deterministic, with no hardware/network/database dependency;
- the **proprietary** brick (Decision 2 mandates building it in-house);
- the definition of the central **`Frame`** contract consumed by everything downstream.

I then defined the **interfaces** (`Frame` schema, `RawPayload`, `CorruptedPayloadError`,
`ProtocolAdapter` ABC) and a **5-phase TDD plan**, and recorded **Decisions 5 to 8**.

### 6. TDD implementation

I implemented test-first (`red → green → refactor`):

1. the `Frame` schema (strict Pydantic v2) and `CorruptedPayloadError`;
2. `ModbusRtuAdapter` (FC 03);
3. extraction of shared logic → `modbus_common.py`;
4. `ModbusTcpAdapter` (MBAP header);
5. `DlmsAdapter` → **deferred** to a dedicated phase (Decision 9, protocol too large).

### 7. Virtual test bench

I built a **deterministic 50-energy-meter simulator** (Modbus RTU/TCP) in `testbench/`, then
tested the **full southbound chain**: simulator → adapter → `Frame`.

### 8. Edge Analytics PS

I implemented the **software data reduction**: time-window aggregation (RMS / min / max / mean)
plus deduplication, turning **N frames → 1 frame** (the −75% volume KPI). Decision 10 records
the output convention.

---

## Part 2 — The code (summary)

### Code layout

```text
projects/edgestream-gw/
├── src/
│   ├── protocol-adapters/
│   │   └── protocol_adapters/      (frame, errors, base, modbus_common, modbus_rtu, modbus_tcp)
│   └── edge-analytics/ps/
│       └── edge_analytics_ps/      (stats, aggregate, window)
└── testbench/
    └── meter_simulator/            (meters, frame_builders)
```

### 1. `protocol_adapters/` — Fail-Fast normalization

**`frame.py`** — the canonical data model, strict Pydantic v2 (`extra="forbid"`):

- `Source`: `device_id`, `protocol` (modbus_rtu/tcp/dlms_cosem), `unit_id` (0–247).
- `Measurement`: `name`, `value`, `unit`, `quality`.
- `Frame`: `frame_id` (UUID), `source`, `collected_at`, `measurements` (≥ 1).

This is **the central object** flowing through the whole system: adapters produce it,
Edge Analytics aggregates it, publishers will forward it to the Cloud.

**`errors.py`** — `CorruptedPayloadError`, the proprietary Fail-Fast exception, carrying a
structured `reason_code` (`TRUNCATED`, `BAD_CRC`, `WRONG_FC`, `INCOMPLETE_ARRAY`,
`OUT_OF_RANGE`, `BAD_UNIT_ID`, `WRONG_PROTOCOL`).

**`base.py`** — the input contract:

- `RawPayload` (dataclass): `protocol`, `device_id`, `unit_id`, `collected_at`, `data`
  (the raw bytes of the full frame).
- `ProtocolAdapter` (abstract class): a single method `parse(payload) -> Frame`.

**`modbus_common.py`** — the logic shared between RTU and TCP:

- `RegisterDefinition`: mapping of one register to a measurement (`name`, `unit`, `scale`,
  `min_value`, `max_value`).
- `decode_holding_registers(...)`: validates the FC 03 response (function code, byte count,
  register count) then **decodes** the 16-bit big-endian registers, applies scale and bounds,
  and builds the list of `Measurement`s.

**`modbus_rtu.py`** — `ModbusRtuAdapter`:

- Checks protocol, `unit_id`, length, then the **CRC-16** (`crc16` function).
- Extracts the registers and delegates to `decode_holding_registers`.
- Builds and returns a `Frame`.

**`modbus_tcp.py`** — `ModbusTcpAdapter`:

- Same principle, but parses the **MBAP** header (transaction_id, protocol_id, length,
  unit_id) instead of the CRC (TCP handles integrity at the transport layer).

**Associated tests** (38 tests): schema, happy path, every Fail-Fast case, property-based
tests (hypothesis: "arbitrary bytes → no exception other than `CorruptedPayloadError`, never an
invalid `Frame`"), and mocked integration.

### 2. `testbench/` — the 50-meter simulator

**`meter_simulator/meters.py`**:

- `STANDARD_REGISTER_MAP`: 4 shared registers (voltage, current, power, energy).
- `EnergyMeter`: a **deterministic** meter (random seed) with realistic drift (Gaussian
  noise); `sample()` returns the 4 raw values.
- `MeterFleet`: a fleet of 50 meters (unique ids, derived seeds).

**`meter_simulator/frame_builders.py`**:

- `build_rtu_response(...)`: builds a valid RTU FC 03 frame (with CRC, reusing `crc16`).
- `build_tcp_response(...)`: builds a valid TCP FC 03 frame (MBAP header).

**Associated tests** (9 tests): fleet size, uniqueness, determinism, value bounds, and the
**end-to-end southbound chain** (simulator → adapter → `Frame`) over RTU and TCP, plus a
5,000-frame load test.

### 3. `edge-analytics/ps/` — data reduction

**`stats.py`**:

- `Aggregate` (dataclass): `count`, `mean`, `rms`, `min`, `max`, `last` per quantity.
- `compute_stats(frames)`: groups measurements by name and computes those statistics.

**`aggregate.py`**:

- `aggregate_window(frames, reducer="rms")`: reduces **N frames → 1 aggregated frame** (per
  quantity: `<name>` = RMS, `<name>.min`, `<name>.max`). This is the −75% KPI mechanism.
- `dedupe(frames)`: drops consecutive identical frames.

**`window.py`**:

- `WindowAggregator`: a **stateful** aggregator that buffers frames and flushes one aggregated
  frame per time window (deterministic on `collected_at`, not wall-clock).

**Associated tests** (19 tests, 100% coverage): statistics, reduction, dedup, windows.

### End-to-end data flow

```text
MeterFleet (50 meters)
   └─> sample() → raw values
        └─> build_rtu_response / build_tcp_response → bytes (ADU)
             └─> ModbusRtuAdapter / ModbusTcpAdapter.parse()
                  └─> Frame (normalized + validated object)
                       └─> aggregate_window() / WindowAggregator
                            └─> aggregated Frame (1 for N) → Cloud
```

---

## Current state (numbers)

- **66 passing tests** in total: 38 (adapters) + 9 (test bench) + 19 (Edge Analytics PS).
- **Coverage**: 100% on both adapters, 100% on Edge Analytics PS.
- **Recorded decisions**: 1 to 10 (in `design/decision-log.md`).

## How to run the tests

```bash
# protocol-adapters
cd projects/edgestream-gw/src/protocol-adapters && .venv/bin/pytest

# edge-analytics/ps (reuses the protocol-adapters venv)
cd projects/edgestream-gw/src/edge-analytics/ps && ../../protocol-adapters/.venv/bin/python -m pytest

# test bench (reuses the protocol-adapters venv)
cd projects/edgestream-gw/testbench && ../src/protocol-adapters/.venv/bin/python -m pytest
```

## Next steps

1. End-to-end measurement of the **−75% KPI** (simulator → adapters → aggregation) in
   `performance/`.
2. `DlmsAdapter` (dedicated spec phase, Decision 9).
3. Ingestion Core, Northbound Publishers, Store-and-Forward, Local Action Engine, PL (FPGA).
4. Specifications of Fog-Crypto Core and NetSentry-IoT.
