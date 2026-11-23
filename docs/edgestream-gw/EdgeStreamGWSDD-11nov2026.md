> Snapshot of projects/edgestream-gw/design/SDD.md — 11 Nov 2026

# EdgeStream-GW — SDD IEEE 1016 (summary)

Full document: `docs/EdgeStream-GW SYSTEM AND SOFTWARE DESIGN DESCRIPTION.pdf`.
This page is the maintained Markdown summary, the source of truth as development proceeds.

## 1. Overview

Industrial IoT gateway between sensors/meters/PLCs and the Cloud, processing real-time
streams locally. Methodological framework CMMI L3: V-Model (macro) + TDD (micro) +
CBSE (integration). KPI: −75% volume, < 50 ms actuation.

## 2. Key definitions

- **Frame** — standardized internal JSON object representing parsed telemetry.
- **ActionCommand** — strict structure of an immediate hardware write command (e.g. Modbus FC 05).
- **Fail-Fast** — immediate, explicit failure on corrupted data, without silent "repair".
- **CorruptedPayloadError** — proprietary exception raised by the protocol adapters.
- **Edge Analytics** — logical PS/PL construct performing data reduction.
- **Northbound Publishers** — modules publishing telemetry to Cloud/SCADA.
- **AXI Bus** — internal high-bandwidth bus between PS (software) and PL (FPGA).
- **Sparkplug B** — industrial MQTT spec (namespace, states, Protobuf payload).

## 3. Architectural viewpoints

- **3.1 Containerization**: Docker, isolated microservices, secure OTA.
- **3.2 Network boundaries**: synchronous south (Modbus, DLMS/COSEM); asynchronous north
  (MQTT + Sparkplug B, OPC UA client-server and PubSub).
- **3.3 CBSE**: Build vs Reuse qualification of components.
- **3.4 PS/PL partitioning**: PS = async (Docker, asyncio, MQTT/OPC UA); PL = deterministic
  (filtering, FFT, low-latency triggers); AXI + interrupt interfaces.

## 4. Modular pipeline

South Drivers → Protocol Adapters → Edge Analytics (PL filtering / PS aggregation) →
Ingestion Core → Northbound Publishers.

## 5. Resilience

- **5.1 Local loop**: PL detects threshold breach → interrupt → PS dispatches the
  `ActionCommand` < 50 ms.
- **5.2 Store-and-Forward**: offline SQLite buffer, replay on reconnection.

## 6. Decisions

See [`decision-log.md`](decision-log.md).

## 7. Traceability

See [`../requirements/RTM.md`](../requirements/RTM.md).
