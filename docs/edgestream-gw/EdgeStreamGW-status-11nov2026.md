# EdgeStream-GW — Project Status

**11 November 2026** · Helveticore OÜ (Tallinn, Estonia)

| | |
| --- | --- |
| **Project** | EdgeStream-GW — IoT Gateway & Edge Analytics |
| **Portfolio position** | Strategic triptych #1 (Smart Grid) |
| **Maturity** | CMMI-DEV Level 3 "Defined" |
| **Current milestone** | Milestone 1 sealed — volume-reduction KPI proven |
| **Overall status** | ✅ Baseline & KPI proven · ⬜ production pipeline next |
| **Hardware target** | Puzhi ZU2CG / ZU3EG (Zynq UltraScale+) |

---

## Status at a glance

| Area | State |
| --- | --- |
| Protocol adapters (Modbus RTU + TCP) | ✅ Done — 38 tests, 99 % coverage |
| Edge Analytics PS (aggregation / dedup) | ✅ Done — 19 tests, 100 % coverage |
| Virtual 50-meter test bench | ✅ Done — 9 tests, deterministic |
| −75 % volume-reduction KPI | ✅ Proven — measured **96.07 %** |
| Ingestion Core (async broker) | ⬜ Milestone 2 |
| Northbound MQTT / Sparkplug B | ⬜ Milestone 3 |
| Store-and-Forward (SQLite) | ⬜ Milestone 4 |
| Local Action Engine (< 50 ms) | ⬜ Milestone 5 |
| Deployment (Docker / OTA) | ⬜ Milestone 6 |
| DLMS/COSEM adapter | ⬜ Milestone 7 |
| Edge Analytics PL (FPGA) + PS/PL | ⬜ Milestone 8 |

**Bottom line:** the gateway's core value — turning a high-frequency meter stream into a
small, clean, normalized stream — is implemented, tested, and *measured*. What remains is the
production pipeline around it (routing, publication, offline resilience, deployment).

---

## What EdgeStream-GW is

An ultra-lightweight industrial software gateway that sits between physical perception nodes
(meters, sensors, PLCs) and the Cloud. It reads raw time-series data, normalizes it into one
strict shared `Frame` object, and shrinks it locally before publication — so the Cloud receives
far less data while the important information is preserved.

Two hard KPIs drive the design:

- **−75 %** data volume transmitted to the Cloud (target; measured **96.07 %**).
- Local actuation latency **< 50 ms** (fast path, no Cloud round-trip — Milestone 5).

---

## Done (verified)

- **Milestone 0 — Baseline** (`milestone-0-baseline`)
  - Fail-Fast protocol adapters: `ModbusRtuAdapter` + `ModbusTcpAdapter` behind one
    `ProtocolAdapter` interface.
  - Strict Pydantic v2 `Frame` schema (`extra="forbid"`, bounded fields, non-empty measurements).
  - Edge Analytics PS: `compute_stats`, `aggregate_window`, `dedupe`, `WindowAggregator`.
  - Deterministic 50-energy-meter virtual test bench.
  - Technical report generator (`makeTRM` → `.docx`).

- **Milestone 1 — Volume-reduction KPI** (`milestone-1-volume-kpi`)
  - End-to-end measurement: `simulator → adapter → Frame → WindowAggregator`.
  - Measured **96.07 %** northbound byte reduction (target ≥ 75 %), stable across 5 seeds.

---

## Verification evidence

| Suite | Tests | Coverage |
| --- | --- | --- |
| protocol-adapters | 38 passed | 99 % (2 defensive lines missed) |
| edge-analytics/ps | 19 passed | 100 % |
| testbench | 9 passed | — (integration) |
| **Total** | **66 passed** | |

KPI measurement (Milestone 1), 50 meters × 300 s @ 1 Hz, 60 s RMS window:

| Metric | Raw | Aggregated | Reduction |
| --- | --- | --- | --- |
| Frames | 15 000 | 250 | **98.33 %** |
| Measurements | 60 000 | 3 000 | **95.00 %** |
| JSON bytes (mean) | 6 666 214 | 262 004 | **96.07 %** |

---

## Reproduce it yourself

```bash
# run all tests (expect 66 passed)
cd projects/edgestream-gw/src/protocol-adapters && .venv/bin/pytest -q     # 38
cd projects/edgestream-gw/src/edge-analytics/ps && \
  ../../protocol-adapters/.venv/bin/python -m pytest -q                     # 19
cd projects/edgestream-gw/testbench && \
  ../src/protocol-adapters/.venv/bin/python -m pytest -q                    # 9

# re-measure the KPI
cd projects/edgestream-gw/performance && \
  ../src/protocol-adapters/.venv/bin/python measure_volume_reduction.py
#   → byte_reduction_pct ≈ 96.07 %, pass: true
```

---

## Roadmap

| # | Milestone | Status | Tag | Exit criteria |
| --- | --- | --- | --- | --- |
| 0 | Baseline | ✅ Done | `milestone-0-baseline` | 66 tests pass; report regenerable |
| 1 | Volume-reduction KPI | ✅ Done | `milestone-1-volume-kpi` | ≥ 75 % reduction measured & archived |
| 2 | Ingestion Core | ⬜ Next | `milestone-2-ingestion-core` | Async broker; lossless delivery + back-pressure tests |
| 3 | Northbound MQTT + Sparkplug B | ⬜ Pending | `milestone-3-northbound-mqtt` | `Frame` adapter vs local Mosquitto |
| 4 | Store-and-Forward SQLite | ⬜ Pending | `milestone-4-store-forward` | Simulated outage + ordered replay (REQ-002) |
| 5 | Local Action Engine < 50 ms | ⬜ Pending | `milestone-5-action-engine` | p95/max latency < 50 ms (REQ-003) |
| 6 | Deployment Docker/Compose/OTA | ⬜ Pending | `milestone-6-deployment` | `docker compose up` zero-config (REQ-005/006) |
| 7 | DLMS/COSEM adapter | ⬜ Pending | `milestone-7-dlms` | Dedicated spec phase (Decision 9) |
| 8 | Edge Analytics PL + PS/PL | ⬜ Pending | `milestone-8-pl-integration` | RTL/HLS filtering on Puzhi board |
| 9 | Fog-Crypto Core spec | ⬜ Pending | `milestone-9-fog-crypto-spec` | Requirements/design/testbench plan |
| 10 | NetSentry-IoT spec | ⬜ Pending | `milestone-10-netsentry-spec` | Requirements/design/testbench plan |

---

## Honest framing: what is *not* there yet

At Milestone 1 this is a **proven building block, not a deployable product**. It reads
*simulated* meters and shrinks data. Missing before production: south drivers (real polling),
ingestion-core routing, northbound publication (MQTT/OPC UA), store-and-forward, the local
action loop, and deployment. Without store-and-forward and northbound, the gateway has no way
to send data or survive a network outage.

Known hardening items before production (full list in the technical report):

- Observability and a boundary policy (log + quarantine malformed frames).
- Clock validation, bounded buffers, data-quality flags (`stale`/`suspect`).
- Concurrency (per-device `asyncio`), external configuration, TLS + authn.
- Failure-injection and soak tests; real-hardware calibration.

---

## Key artifacts

- Requirements: [`REQ-11nov2026.md`](REQ-11nov2026.md) · [`RTM-11nov2026.md`](RTM-11nov2026.md)
- Design: [`SDD-11nov2026.md`](SDD-11nov2026.md) · [`decision-log-11nov2026.md`](decision-log-11nov2026.md)
- KPI report: [`volume_reduction_report-11nov2026.md`](volume_reduction_report-11nov2026.md)
- Bill of materials: [`SBOM-11nov2026.md`](SBOM-11nov2026.md)
- Beginner tutorial: [`tutorial-milestone-1-11nov2026.md`](tutorial-milestone-1-11nov2026.md)
- Companion document: [`EdgeStream-rapport-technique-11nov2026.md`](EdgeStream-rapport-technique-11nov2026.md)

*Status snapshot prepared for online publication — 11 November 2026.*
