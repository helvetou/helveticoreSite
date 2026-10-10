# Helveticore Portfolio — Current state

_Last updated: 2026-09-24_

## Done

- Portfolio scaffold (CMMI L3): `process/`, `projects/{edgestream-gw, fog-crypto-core, netsentry-iot}`.
- All documentation and READMEs translated to English.
- Source documents converted to PDF in `docs/`.
- EdgeStream-GW — Protocol Adapters: interface spec, TDD plan, decisions 5–10 recorded.
- EdgeStream-GW — Protocol Adapters implemented test-first (`ModbusRtuAdapter` + `ModbusTcpAdapter`,
  38 tests, 100% coverage on both adapters).
- EdgeStream-GW — virtual test bench: deterministic 50-meter Modbus simulator (9 tests).
- EdgeStream-GW — Edge Analytics PS: window aggregation + dedup (19 tests, 100% coverage).

## In progress — EdgeStream-GW implementation

- **Protocol Adapters** (`src/protocol-adapters/`): RTU + TCP done; DLMS deferred (Decision 9).
- **Edge Analytics PS** (`src/edge-analytics/ps/`): `compute_stats`, `aggregate_window`,
  `dedupe`, `WindowAggregator` — targets the −75% volume KPI (N frames → 1).
- **Virtual test bench** (`testbench/`): 50-meter fleet simulator + southbound chain tests.

## Next steps

1. End-to-end reduction measurement: simulator → adapters → `aggregate_window` → quantify the
   −75% volume KPI in `performance/`.
2. `DlmsAdapter` — dedicated specification phase (Decision 9).
3. Then: Ingestion Core, Northbound Publishers, Store-and-Forward, Local Action Engine, PL (FPGA).
4. Portfolio: Fog-Crypto Core and NetSentry-IoT specifications.

## How to run the tests

```bash
# protocol-adapters
cd projects/edgestream-gw/src/protocol-adapters && .venv/bin/pytest

# edge-analytics/ps (reuses the protocol-adapters venv)
cd projects/edgestream-gw/src/edge-analytics/ps && ../../protocol-adapters/.venv/bin/python -m pytest

# virtual test bench (reuses the protocol-adapters venv)
cd projects/edgestream-gw/testbench && ../src/protocol-adapters/.venv/bin/python -m pytest
```
