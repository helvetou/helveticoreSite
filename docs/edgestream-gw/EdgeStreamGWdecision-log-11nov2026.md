> Snapshot of projects/edgestream-gw/design/decision-log.md — 11 Nov 2026

# EdgeStream-GW — Decision log (DAR / IEEE 1016)

## Decision 1 — Protocol collection: Build vs Reuse (South Drivers)

- **Criteria**: development speed, protocol compliance, hardware footprint.
- **Options**: proprietary C/Python drivers vs open-source reuse (`pymodbus`, Gurux DLMS).
- **Decision**: **REUSE**.
- **Rationale**: rebuilding compliant Modbus/DLMS stacks brings no strategic value and risks
  non-compliance. Requirements: REQ-004, REQ-008.

## Decision 2 — Data normalization: Build vs Reuse (Protocol Adapters)

- **Criteria**: "Fail-Fast" handling, TDD compliance, strict JSON schema alignment.
- **Options**: open-source parsers vs proprietary adapters.
- **Decision**: **BUILD FROM SCRATCH**.
- **Rationale**: open-source parsers silently fix bad data or let incomplete arrays through;
  in-house adapters raise `CorruptedPayloadError` and guarantee CMMI L3 quality.
  Requirement: REQ-004.

## Decision 3 — Store-and-Forward database

- **Criteria**: lightweight footprint on edge SSDs, power-loss resistance, open source.
- **Options**: proprietary binary files vs MongoDB vs SQLite.
- **Decision**: **REUSE SQLite**.
- **Rationale**: MongoDB is too heavy for the PS RAM limits; binary files risk corruption on
  power loss; SQLite is serverless, ACID and edge-appropriate. Requirements: REQ-002, REQ-008.

## Decision 4 — HW/SW partitioning boundary (Zynq UltraScale+)

- **Criteria**: < 50 ms response latency, CPU load optimization.
- **Options**: 100% software evaluation vs PS/PL split.
- **Decision**: **PS/PL SPLIT**.
- **Rationale**: routing high-frequency continuous signals through the Linux kernel (PS)
  introduces non-deterministic OS latency; delegating filtering and first threshold breaches
  to the PL guarantees sub-millisecond detection, leaving the PS to route only the
  asynchronous `ActionCommand`. Requirement: REQ-003.

## Decision 5 — First module for detailed specification

- **Criteria**: ease of implementation, testability (TDD), absence of external dependencies,
  strategic value, position in the dependency graph.
- **Options**: Protocol Adapters vs Edge Analytics PS vs Store-and-Forward vs modules of
  Fog-Crypto Core / NetSentry-IoT.
- **Decision**: **Protocol Adapters (EdgeStream-GW)** as the first module to be specified in detail.
- **Rationale**: pure Python transformation (`bytes → Frame`), deterministic and TDD-friendly,
  no hardware/network/database dependency; it is the proprietary brick mandated by Decision 2
  (build in-house); it defines the central `Frame` contract consumed by all downstream components.
- **Impacted requirements**: REQ-004 (Fail-Fast), REQ-008 (embedded footprint).
- **Status**: Accepted.

## Decision 6 — Schema validation engine

- **Criteria**: strictness, idiomatic Python, TDD ergonomics, performance.
- **Options**: Pydantic v2 vs pure `jsonschema`.
- **Decision**: **Pydantic v2** (strict mode, `extra="forbid"`).
- **Rationale**: type-safe, fast (compile-to-core), first-class with pytest/hypothesis, strict
  enforcement including bounded value ranges.
- **Status**: Accepted.

## Decision 7 — First protocol to implement

- **Criteria**: simplicity, alignment with the virtual test bench (50 energy meters),
  availability of reference vectors.
- **Options**: Modbus RTU vs Modbus TCP vs DLMS/COSEM.
- **Decision**: **Modbus RTU first** (FC 03 "read holding registers"), then Modbus TCP, then
  DLMS/COSEM, all behind the same `ProtocolAdapter` interface.
- **Rationale**: Modbus RTU is the simplest and matches the 50-meter bench; `pymodbus` provides
  reference vectors (Decision 1 — REUSE).
- **Status**: Accepted.

## Decision 8 — TDD tooling

- **Criteria**: deterministic unit testing, property-based testing, coverage, linting.
- **Options**: pytest + hypothesis vs alternative stacks.
- **Decision**: **pytest + hypothesis + pydantic v2 + pytest-cov + ruff**.
- **Rationale**: `hypothesis` enforces the "no other exception / no invalid Frame" invariant;
  `pytest-cov` for branch coverage; `ruff` for lint.
- **Status**: Accepted.

## Decision 9 — DLMS/COSEM adapter: defer to a dedicated specification phase

- **Criteria**: scope, protocol complexity, value delivered per iteration.
- **Options**: implement a full DLMS/COSEM adapter now vs defer it to a dedicated spec phase.
- **Decision**: **DEFER**. Implement Modbus RTU + TCP first (done); treat DLMS/COSEM as its own
  specification phase (framing choice HDLC vs COSEM-TCP, A-XDR decoding, OBIS code mapping).
- **Rationale**: DLMS/COSEM is a substantial protocol; a rushed parser would violate the
  Fail-Fast quality guarantees. The `ProtocolAdapter` interface already accommodates it.
- **Status**: Accepted.

## Decision 10 — Edge Analytics PS aggregation output convention

- **Criteria**: keep the canonical `Frame` schema stable, preserve RMS/min/max trends,
  minimize churn and downstream impact.
- **Options**: (a) extend the `Frame`/`Measurement` schema with stats fields; (b) emit, per
  quantity, a primary measurement plus `.min`/`.max` suffixed measurements.
- **Decision**: **(b)** — one aggregated `Frame` per window; per quantity emit `<name>`
  (reducer, default `rms`), `<name>.min`, `<name>.max`. Reducer configurable among
  `rms` / `mean` / `last`.
- **Rationale**: keeps the canonical schema unchanged (no breaking change, no RTM churn) while
  preserving the SDD's "RMS, min/max trends"; N frames → 1 frame realizes the −75% volume KPI.
- **Impacted requirements**: REQ-001b.
- **Status**: Accepted.
