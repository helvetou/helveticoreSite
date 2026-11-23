> Snapshot of projects/edgestream-gw/requirements/REQ.md — 11 Nov 2026

# EdgeStream-GW — Requirements (RDM)

Consolidated extracts from the IEEE 1016 SDD. IDs stay aligned with the source document.

## Core requirements

- **REQ-001a — Hardware data reduction (PL)**: digital noise filtering and FFT executed on
  the FPGA fabric continuously. Trace: `design/SDD.md` §4 (Edge Analytics PL).
- **REQ-001b — Software data reduction (PS)**: time-window aggregation (RMS, min/max,
  deduplication) on `Frame` objects. Trace: §4 (Edge Analytics PS).
  *(REQ-001a + REQ-001b together satisfy the overall ≥ 75% volume-reduction KPI.)*
- **REQ-002 — Offline resilience**: local buffering (SQLite) and sequential, intelligently
  throttled replay on reconnection. Trace: §5.2 (Store-and-Forward).
- **REQ-003 — Actuation < 50 ms**: local PS/PL loop triggering an `ActionCommand` without any
  Cloud dependency. Trace: §3.4 & §5.1.

## Derived requirements

- **REQ-004 — Fail-Fast**: any corrupted/incomplete payload is rejected immediately
  (`CorruptedPayloadError` raised by the adapters), never silently "repaired".
- **REQ-005 — Zero-configuration deployment**: Docker-containerized stack deployable without
  manual configuration on embedded Linux.
- **REQ-006 — Secure OTA updates**: container-isolated microservice updates without stopping
  collection.
- **REQ-007 — Northbound interoperability**: MQTT publication with Sparkplug B (Protobuf) and
  OPC UA (client-server + PubSub) for IT/OT convergence.
- **REQ-008 — Embedded footprint**: RAM/storage footprint compatible with a Zynq UltraScale+
  (PS); the database must be lightweight and power-loss resistant.

## Module requirements — Protocol Adapters (REQ-004 decomposition)

Derived from REQ-004 (Fail-Fast). Interface contract: `design/interface-spec.md`.

- **REQ-004.1 — Strict `Frame` schema**: the `Frame` object is validated by a strict Pydantic v2
  model (`extra="forbid"`): required fields, exact types, non-empty `measurements`, bounded
  ranges. *Acceptance*: any invalid payload is rejected by the schema.
- **REQ-004.2 — Atomic Fail-Fast**: `parse()` returns a fully-valid `Frame` **or** raises
  `CorruptedPayloadError`; never a partial or "repaired" frame. *Acceptance*: 100% of corrupted
  payloads rejected.
- **REQ-004.3 — Structured error**: `CorruptedPayloadError` carries a `reason_code`
  (`TRUNCATED`, `BAD_CRC`, `WRONG_FC`, `INCOMPLETE_ARRAY`, `OUT_OF_RANGE`, `BAD_UNIT_ID`,
  `WRONG_PROTOCOL`).
  *Acceptance*: each corruption class maps to its documented code.
- **REQ-004.4 — Modbus RTU (FC 03) decoding**: decode "read holding registers" responses into
  `Measurement`s (big-endian, scaled, mapped to name/unit). *Acceptance*: a valid FC 03
  response yields the expected measurements.
- **REQ-004.5 — Purity**: deterministic (same input → same output), no I/O, no wall-clock
  (timestamp injected via `RawPayload.collected_at`). *Acceptance*: `parse` is a pure function.
- **REQ-004.6 — Exception isolation**: `parse()` never lets any exception other than
  `CorruptedPayloadError` escape. *Acceptance*: property-based tests over arbitrary bytes hold
  the invariant.

## Industrial constraints

- High polling rates and continuous streams (real-time, without a deterministic OS on the PS).
- Network and power outages possible at any time.
- Smart Grid metering environment: many nodes, heterogeneous protocols.

## Out of scope

- Cloud / back-office management (data reception beyond northbound publication).
- Development of proprietary Modbus/DLMS stacks (reused, cf. decision log).
