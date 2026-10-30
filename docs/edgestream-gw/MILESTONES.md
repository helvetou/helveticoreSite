# MILESTONES — Helveticore EdgeStream-GW roadmap

Sequential, reviewable execution checkpoints. Each milestone is sealed as one
atomic commit on `main` and tagged `milestone-<Number>-<description>`. Navigate
with `git checkout <tag>`; back-off with `git reset --hard <previous tag>`.

## Governance

- Audit → confirm next milestone → execute → hand back → accept or back-off.
- Exit criteria must be verified (tests / measurement) before a milestone is sealed.

## Roadmap

| # | Milestone | Status | Tag | Exit criteria |
| --- | --- | --- | --- | --- |
| 0 | Baseline | ✅ Done | `milestone-0-baseline` | 66 tests pass; report `.docx` regenerable |
| 1 | Volume-reduction KPI | ✅ Done | `milestone-1-volume-kpi` | ≥ 75 % northbound reduction measured & archived in `performance/` |
| 2 | Ingestion Core | ⬜ Pending | `milestone-2-ingestion-core` | Async broker, TDD; lossless delivery + back-pressure tests |
| 3 | Northbound MQTT + Sparkplug B | ⬜ Pending | `milestone-3-northbound-mqtt` | `Frame` adapter, integration test vs local Mosquitto |
| 4 | Store-and-Forward SQLite | ⬜ Pending | `milestone-4-store-forward` | Simulated outage + ordered replay (REQ-002) |
| 5 | Local Action Engine PS < 50 ms | ⬜ Pending | `milestone-5-action-engine` | p95/max latency < 50 ms bench (REQ-003) |
| 6 | Deployment Docker/Compose/OTA | ⬜ Pending | `milestone-6-deployment` | `docker compose up` zero-config (REQ-005/006) |
| 7 | DLMS/COSEM adapter | ⬜ Pending | `milestone-7-dlms` | Dedicated spec phase (Decision 9) + adapter behind `ProtocolAdapter` |
| 8 | Edge Analytics PL + PS/PL integration | ⬜ Pending | `milestone-8-pl-integration` | RTL/HLS filtering + PS/PL integration on Puzhi board |
| 9 | Fog-Crypto Core spec | ⬜ Pending | `milestone-9-fog-crypto-spec` | Requirements/design/testbench plan |
| 10 | NetSentry-IoT spec | ⬜ Pending | `milestone-10-netsentry-spec` | Requirements/design/testbench plan |

## Convention

- Tag format: `milestone-<Number>-<description>` (e.g. `milestone-1-volume-kpi`).
- One atomic commit per milestone; working tree clean before tagging.
