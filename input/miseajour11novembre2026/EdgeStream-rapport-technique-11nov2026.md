# EdgeStream-GW — Technical Report

**11 November 2026** · Helveticore OÜ (Tallinn, Estonia)

*EdgeStream-GW: an ultra-lightweight industrial IoT gateway and edge-analytics layer for
Smart Grid metering, engineered under a CMMI Level 3 "Defined" process.*

| | |
| --- | --- |
| **Project** | EdgeStream-GW — IoT Gateway & Edge Analytics |
| **Hardware target** | Puzhi ZU2CG / ZU3EG (Zynq UltraScale+, PS/PL) |
| **Methodology** | CMMI-DEV Level 3 — V-Model · TDD · CBSE |
| **Report scope** | Milestone 0 (baseline) and Milestone 1 (KPI) |
| **Status** | Baseline + −75 % KPI proven and verified |

---

## Abstract

EdgeStream-GW intercepts raw time-series data from industrial meters, normalizes it into a
single strict `Frame` contract, and aggregates it at the edge so the Cloud receives a fraction
of the original volume. This report documents the two completed milestones: the Fail-Fast
protocol adapters and edge-analytics core (Milestone 0), and the measured proof of the
data-reduction KPI (Milestone 1). Verification evidence: **66 tests passing**, 99 % / 100 %
coverage on the two software modules, and a measured **96.07 %** northbound volume reduction
against a ≥ 75 % target, stable across seeds.

---

## 1. Context

Helveticore OÜ's portfolio is a strategic triptych of three technology bricks:

1. **EdgeStream-GW** — IoT gateway & edge analytics (Smart Grid).
2. **Fog-Crypto Core** — FPGA hardware accelerator (HW/SW co-design, security).
3. **NetSentry-IoT** — active network cybersecurity probe (NIS2 / GDPR).

EdgeStream-GW targets the "hero layer" of a three-layer edge ecosystem: it sits between
physical perception nodes (sensors, meters, PLCs) and the Cloud, processing streams locally to
prevent data bottlenecks in harsh industrial environments.

Two hard KPIs anchor the project:

- **−75 %** of data volume transmitted to the Cloud.
- Local actuation latency **< 50 ms** (fast path, no Cloud round-trip).

---

## 2. Methodology — CMMI Level 3 (Defined)

The project follows a documented, repeatable process expressed through three practices:

| Level | Approach | Role |
| --- | --- | --- |
| Macro-architecture | V-Model | Top-down design, bottom-up validation & verification |
| Micro-architecture | TDD | Test-driven development of proprietary components |
| Integration | CBSE | Qualify and reuse proven open-source components |

**Build-vs-reuse rule:** reuse an open-source component when footprint and latency criteria
are met and compliance is proven (e.g. `pymodbus`, Mosquitto); build in-house any component
requiring strict Fail-Fast behavior, a proprietary schema, or a CMMI L3 quality guarantee. Each
choice is recorded in `design/decision-log.md` (criteria, options, decision, rationale).

Repository artifacts map directly to CMMI practice areas: requirements (RDM), design (TS),
decision log (DAR), test bench (VV), performance (M&A), and Git versioning + immutable docs (CM).

---

## 3. System architecture

Data flows south → north through a modular pipeline:

```
south-drivers  →  protocol-adapters  →  edge-analytics  →  ingestion-core  →  northbound-publishers
 (read meters)     (normalize Frame)    (shrink data)      (route data)      (send to Cloud)
                                      ↘  local-action-engine  (fast path, < 50 ms)
                                      ↘  store-and-forward    (offline queue)
```

| Sub-project | Responsibility | Milestone |
| --- | --- | --- |
| `south-drivers` | Industrial protocol collection (Modbus RTU/TCP, DLMS) — reuse | M2+ |
| `protocol-adapters` | Normalize raw bytes → `Frame` (TDD, Fail-Fast) — build | ✅ M0 |
| `edge-analytics` | Filtering (PL) + aggregation (PS) — the −75 % core | ✅ PS (M0/M1) |
| `ingestion-core` | Async broker routing `Frame`s | ⬜ M2 |
| `northbound-publishers` | MQTT (Sparkplug B) / OPC UA | ⬜ M3 |
| `local-action-engine` | < 50 ms threshold loop + `ActionCommand` dispatch | ⬜ M5 |
| `store-and-forward` | Offline SQLite buffer + replay | ⬜ M4 |
| `deployment` | Docker zero-config + secure OTA | ⬜ M6 |

---

## 4. Requirements (extract)

| ID | Requirement | Status at M1 |
| --- | --- | --- |
| REQ-001a | Hardware data reduction (PL): filtering + FFT on FPGA fabric | ⬜ M8 |
| REQ-001b | Software data reduction (PS): window aggregation on `Frame`s | ✅ proven (96.07 %) |
| REQ-002 | Offline resilience: SQLite buffer + throttled replay | ⬜ M4 |
| REQ-003 | Actuation < 50 ms, no Cloud dependency | ⬜ M5 |
| REQ-004 | Fail-Fast: reject corrupted payloads immediately | ✅ proven |
| REQ-005 | Zero-configuration Docker deployment | ⬜ M6 |
| REQ-006 | Secure OTA updates | ⬜ M6 |
| REQ-007 | Northbound interoperability (MQTT + Sparkplug B, OPC UA) | ⬜ M3 |
| REQ-008 | Embedded footprint (Zynq UltraScale+ PS) | design constraint |

REQ-004 decomposes into REQ-004.1 … REQ-004.6 (strict `Frame` schema, atomic Fail-Fast,
structured `reason_code`, FC-03 decoding, purity, exception isolation).

---

## 5. Implemented components (Milestones 0–1)

### 5.1 Protocol adapters (build, TDD)

- **`Frame` schema** — strict Pydantic v2 models (`Frame`, `Source`, `Measurement`) with
  `extra="forbid"`, bounded `unit_id` (0–247), and non-empty `measurements`.
- **`ProtocolAdapter` interface** — `parse(payload) -> Frame` or raise
  `CorruptedPayloadError`; nothing else.
- **`CorruptedPayloadError`** — structured error carrying a `reason_code`
  (`TRUNCATED`, `BAD_CRC`, `WRONG_FC`, `INCOMPLETE_ARRAY`, `OUT_OF_RANGE`, `BAD_UNIT_ID`,
  `WRONG_PROTOCOL`).
- **`ModbusRtuAdapter`** — CRC16-validated RTU ADU parsing, fail-fast on first violation.
- **`ModbusTcpAdapter`** — MBAP/TCP ADU parsing, shared FC-03 decode via
  `decode_holding_registers`.
- **Purity** — timestamp injected via `RawPayload.collected_at`; no I/O, no wall clock.

### 5.2 Edge Analytics PS (build, TDD)

- **`compute_stats`** — mean/rms/min/max/last/count per quantity.
- **`aggregate_window`** — N frames → 1 aggregated frame, emitting per quantity `<name>`
  (reducer, default `rms`), `<name>.min`, `<name>.max`.
- **`dedupe`** — drops consecutive identical frames.
- **`WindowAggregator`** — deterministic time-window buffering keyed on `collected_at`.

The output convention keeps the canonical `Frame` schema unchanged (Decision 10) — min/max are
expressed as suffixed measurements, not new schema fields.

### 5.3 Virtual test bench (build)

A deterministic 50-energy-meter simulator (`MeterFleet`, seeded `random.Random`), with
frame builders that wrap meter readings into realistic Modbus RTU/TCP ADUs.

---

## 6. Key design decisions (summarized)

1. **South drivers — reuse** proven Modbus/DLMS stacks (`pymodbus`, Gurux).
2. **Protocol adapters — build from scratch** to guarantee Fail-Fast quality.
3. **Store-and-Forward — reuse SQLite** (serverless, ACID, power-loss resistant).
4. **PS/PL split** to guarantee sub-millisecond detection (REQ-003).
5. **First module** = protocol adapters (pure, deterministic, dependency-free).
6. **Schema engine** = Pydantic v2 strict mode.
7. **First protocol** = Modbus RTU (FC 03), then TCP, then DLMS/COSEM.
8. **TDD tooling** = pytest + hypothesis + pytest-cov + ruff.
9. **DLMS/COSEM deferred** to a dedicated specification phase.
10. **Aggregation output convention** = `<name>` + `.min`/`.max` suffixed measurements.

Full rationale in [`decision-log-11nov2026.md`](decision-log-11nov2026.md).

---

## 7. Verification & validation

| Suite | Tests | Coverage |
| --- | --- | --- |
| protocol-adapters | 38 passed | 99 % (2 defensive lines missed) |
| edge-analytics/ps | 19 passed | 100 % |
| testbench | 9 passed | — (integration) |
| **Total** | **66 passed** | |

Property-based tests (hypothesis) enforce the invariant: for arbitrary byte input, `parse`
returns a valid `Frame` **or** raises `CorruptedPayloadError` — never any other error, never a
crash. Contract tests exercise the mocked south-driver → adapter → ingestion-core boundary.

---

## 8. KPI measurement — volume reduction (REQ-001b)

**Scenario:** 50 meters × 300 s at 1 Hz → 15 000 raw frames; per-meter `WindowAggregator`
with a 60 s RMS window; volume measured as UTF-8 JSON bytes of the normalized `Frame` stream.

| Metric | Raw | Aggregated | Reduction |
| --- | --- | --- | --- |
| Frames | 15 000 | 250 | **98.33 %** |
| Measurements | 60 000 | 3 000 | **95.00 %** |
| JSON bytes (mean) | 6 666 214 | 262 004 | **96.07 %** |

Byte-reduction across 5 seeds: min **96.0689 %**, mean **96.0696 %**, max **96.0701 %** —
stable and structural (a 60 s window collapses 60 frames per meter into 1).

**Conclusion: PASS** — 96.07 % exceeds the ≥ 75 % target by a wide margin, realizing REQ-001b
and the portfolio KPI. Raw per-seed data: [`volume_reduction_results.json`](../../projects/edgestream-gw/performance/volume_reduction_results.json).

---

## 9. Risks & mitigations

| Risk | Mitigation | Decision |
| --- | --- | --- |
| PS/PL latency non-determinism | Hardware partitioning of filtering/FFT | 4 |
| Data corruption on power loss | SQLite ACID | 3 |
| Protocol non-compliance | Reuse proven stacks | 1 |
| Silent repair of bad data | In-house Fail-Fast adapters | 2 |

Known production hardening items (observability, boundary policy, clock validation, bounded
buffers, concurrency, external config, TLS/authn, fault injection, real-hardware calibration)
are catalogued in the roadmap's gap analysis.

---

## 10. Roadmap

| # | Milestone | Status | Exit criteria |
| --- | --- | --- | --- |
| 0 | Baseline | ✅ | 66 tests pass; report regenerable |
| 1 | Volume-reduction KPI | ✅ | ≥ 75 % reduction measured & archived |
| 2 | Ingestion Core | ⬜ | Async broker; lossless delivery + back-pressure tests |
| 3 | Northbound MQTT + Sparkplug B | ⬜ | `Frame` adapter vs local Mosquitto |
| 4 | Store-and-Forward SQLite | ⬜ | Simulated outage + ordered replay (REQ-002) |
| 5 | Local Action Engine < 50 ms | ⬜ | p95/max latency < 50 ms (REQ-003) |
| 6 | Deployment Docker/Compose/OTA | ⬜ | `docker compose up` zero-config (REQ-005/006) |
| 7 | DLMS/COSEM adapter | ⬜ | Dedicated spec phase (Decision 9) |
| 8 | Edge Analytics PL + PS/PL | ⬜ | RTL/HLS filtering on Puzhi board |
| 9 | Fog-Crypto Core spec | ⬜ | Requirements/design/testbench plan |
| 10 | NetSentry-IoT spec | ⬜ | Requirements/design/testbench plan |

---

## Appendix A — Software bill of materials (summary)

| Item | Value |
| --- | --- |
| Language | Python ≥ 3.10 (verified 3.14.4) |
| Runtime dependency | `pydantic` ≥ 2.10 (verified 2.13.5) |
| Dev dependencies | `pytest` ≥ 7, `hypothesis` ≥ 6, `pytest-cov`, `ruff` |
| Package | `edgestream-protocol-adapters` v0.1.0 |

## Appendix B — Reproducibility

```bash
cd projects/edgestream-gw/src/protocol-adapters && .venv/bin/pytest -q      # 38 passed
cd projects/edgestream-gw/src/edge-analytics/ps && \
  ../../protocol-adapters/.venv/bin/python -m pytest -q                      # 19 passed
cd projects/edgestream-gw/testbench && \
  ../src/protocol-adapters/.venv/bin/python -m pytest -q                     # 9 passed

# re-measure the KPI
cd projects/edgestream-gw/performance && \
  ../src/protocol-adapters/.venv/bin/python measure_volume_reduction.py
```

---

*Technical report prepared for online publication — 11 November 2026. Companion status
document: [`EdgeStreamGW-status-11nov2026.md`](EdgeStreamGW-status-11nov2026.md).*
