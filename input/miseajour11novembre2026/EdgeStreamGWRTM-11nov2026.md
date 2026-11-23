> Snapshot of projects/edgestream-gw/requirements/RTM.md — 11 Nov 2026

# EdgeStream-GW — Requirements Traceability Matrix (RTM)

| Requirement | Design (§ SDD) | Component (src/) | Verification (testbench/) | KPI |
| --- | --- | --- | --- | --- |
| REQ-001a | §4 Edge Analytics PL | `edge-analytics/pl/` | RTL / HLS simulation (FFT + filter) | −75% volume |
| REQ-001b | §4 Edge Analytics PS | `edge-analytics/ps/` | aggregation tests (TDD) | −75% volume |
| REQ-002 | §5.2 Store-and-Forward | `store-and-forward/` | simulated outage + replay | resilience |
| REQ-003 | §3.4 & §5.1 Action Engine | `local-action-engine/{pl,ps}/` | < 50 ms latency bench | < 50 ms |
| REQ-004 | §4 Protocol Adapters | `protocol-adapters/` | corrupted payloads (TDD) | quality |
| REQ-004.1 | interface-spec §2 | `protocol-adapters/frame.py` | test_frame_schema (phase 0) | quality |
| REQ-004.2 | interface-spec §4 | `protocol-adapters/modbus_rtu.py` | test_modbus_rtu (phase 2) | quality |
| REQ-004.3 | interface-spec §3.3 | `protocol-adapters/errors.py` | test_modbus_rtu (phase 2) | quality |
| REQ-004.4 | interface-spec §3 | `protocol-adapters/modbus_rtu.py` | test_modbus_rtu (phase 1) | quality |
| REQ-004.5 | interface-spec §4 | `protocol-adapters/base.py` | test_properties (phase 3) | quality |
| REQ-004.6 | interface-spec §4 | `protocol-adapters/modbus_rtu.py` | test_properties (phase 3) | quality |
| REQ-005 | §3.1 Containerization | `deployment/` | docker-compose deployment | zero-config |
| REQ-006 | §3.1 Containerization | `deployment/` | OTA update test | continuity |
| REQ-007 | §3.2 North boundary | `northbound-publishers/` | Mosquitto + OPC UA client | IT/OT interop |
| REQ-008 | §6 Decision 3 | `store-and-forward/` | RAM/storage measurement | footprint |

> Each row must be verified and checked off in the performance report before any release.
