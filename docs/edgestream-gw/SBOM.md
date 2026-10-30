# Software Bill of Materials — EdgeStream-GW (Milestone 1)

_Date: 2026-10-28 · Scope: all Python source & test files under `projects/edgestream-gw/` · State: Milestone 1 (KPI −75 % proven)_

## 1. Runtime & toolchain

| Item | Value |
| --- | --- |
| Language | Python (requires ≥ 3.10; verified on 3.14.4) |
| Runtime dependency | `pydantic` (≥ 2.10; verified 2.13.5) |
| Dev dependencies | `pytest` (≥ 7), `hypothesis` (≥ 6), `pytest-cov`, `ruff` (line-length 100) |
| Package | `edgestream-protocol-adapters` v0.1.0 |

## 2. Source files (build vs reuse)

Legend: **BUILD** = in-house (TDD, Fail-Fast) · **REUSE** = standard library / 3rd party.

### 2.1 `src/protocol-adapters/` — Protocol Adapters (BUILD)

| File | Contains |
| --- | --- |
| `protocol_adapters/frame.py` | Strict Pydantic v2 models: `Frame`, `Source`, `Measurement` (`extra="forbid"`, bounded `unit_id`, non-empty `measurements`). |
| `protocol_adapters/errors.py` | `CorruptedPayloadError(reason_code, detail, offending_field)` — the Fail-Fast exception. |
| `protocol_adapters/base.py` | `RawPayload` frozen dataclass (input contract) + `ProtocolAdapter` ABC (`parse()`). |
| `protocol_adapters/modbus_common.py` | `RegisterDefinition` + `decode_holding_registers()` (shared FC03 decode + bounds checks). |
| `protocol_adapters/modbus_rtu.py` | `crc16()` + `ModbusRtuAdapter` (RTU ADU parsing, Fail-Fast). |
| `protocol_adapters/modbus_tcp.py` | `ModbusTcpAdapter` (MBAP/TCP ADU parsing, Fail-Fast). |
| `protocol_adapters/__init__.py` | Public API re-exports (`Frame`, `Measurement`, adapters, `crc16`, `RegisterDefinition`, …). |
| `conftest.py` | Pytest bootstrap: makes the package importable. |

### 2.2 `src/edge-analytics/ps/` — Edge Analytics PS (BUILD)

| File | Contains |
| --- | --- |
| `edge_analytics_ps/stats.py` | `Aggregate` dataclass + `compute_stats()` (mean/rms/min/max/last/count). |
| `edge_analytics_ps/aggregate.py` | `aggregate_window()` (N frames → 1) + `dedupe()` (consecutive dedup). |
| `edge_analytics_ps/window.py` | `WindowAggregator` (time-window buffering, deterministic on `collected_at`). |
| `edge_analytics_ps/__init__.py` | Public API re-exports. |
| `conftest.py` | Pytest bootstrap: makes `edge_analytics_ps` + `protocol_adapters` importable. |

### 2.3 `testbench/` — Virtual test bench (BUILD)

| File | Contains |
| --- | --- |
| `meter_simulator/meters.py` | `STANDARD_REGISTER_MAP` (4 registers), `EnergyMeter`, `MeterFleet` (deterministic 50-meter simulator). |
| `meter_simulator/frame_builders.py` | `build_rtu_response()` / `build_tcp_response()` (raw Modbus ADU builders). |
| `meter_simulator/__init__.py` | Public API re-exports. |
| `conftest.py` | Pytest bootstrap: makes `meter_simulator` + `protocol_adapters` importable. |

### 2.4 `performance/` — Measurement (BUILD)

| File | Contains |
| --- | --- |
| `measure_volume_reduction.py` | Measures the −75 % KPI (simulator → adapter → `WindowAggregator` → JSON byte counts), writes `volume_reduction_results.json`. |

### 2.5 `reports/` — Documentation tooling (BUILD)

| File | Contains |
| --- | --- |
| `make_report.py` | python-docx generator for the Word technical report. |

## 3. Test files

### 3.1 `src/protocol-adapters/tests/` — 38 tests

| File | Covers |
| --- | --- |
| `test_frame_schema.py` | Phase 0 — strict schema (required fields, types, `extra`, empty list, `unit_id` bounds). |
| `test_modbus_rtu.py` | Phases 1–2 — RTU happy path + all 7 `reason_code` negatives. |
| `test_modbus_tcp.py` | TCP happy path + MBAP/negatives. |
| `test_properties.py` | Phase 3 — hypothesis invariants (arbitrary bytes never crash; roundtrip). |
| `test_contract.py` | Phase 4 — mocked south-driver → adapter → ingestion-core boundary. |

### 3.2 `src/edge-analytics/ps/tests/` — 19 tests

| File | Covers |
| --- | --- |
| `test_stats.py` | `compute_stats` (empty, single, multiple, grouping). |
| `test_aggregate.py` | `aggregate_window` (empty, bad reducer, mixed sources, N→1, rms/min/max, mean, timestamp). |
| `test_dedupe.py` | `dedupe` (consecutive, non-consecutive, empty, identical). |
| `test_window.py` | `WindowAggregator` (flush on crossing, no flush within, empty flush). |

### 3.3 `testbench/tests/` — 9 tests

| File | Covers |
| --- | --- |
| `test_meter_fleet.py` | Fleet properties (50, unique ids, determinism, bounds). |
| `test_southbound_chain.py` | E2E chain simulator → adapter → Frame (RTU/TCP + 5 000-frame volume). |

## 4. Verification summary (as of 2026-10-28)

| Suite | Tests | Coverage |
| --- | --- | --- |
| protocol-adapters | 38 passed | 99 % (154 stmts, 2 defensive lines missed) |
| edge-analytics/ps | 19 passed | 100 % (90 stmts) |
| testbench | 9 passed | — (integration) |
| **Total** | **66 passed** | |

KPI (Milestone 1): **96.07 %** northbound volume reduction (target ≥ 75 %).
