# Helveticore Methodology Charter — CMMI Level 3 (Defined)

## 1. Scope

Helveticore OÜ commits to delivering its technology bricks at **CMMI-DEV v2.0, Level 3
"Defined"** maturity. The process is defined, documented and reused identically across
projects.

## 2. Hybrid lifecycle

| Level | Approach | Role |
| --- | --- | --- |
| Macro-architecture | V-Model | Top-down design, bottom-up validation & verification |
| Micro-architecture | TDD | Test-driven development of proprietary components |
| Integration | CBSE | Qualification and reuse of proven open-source components |

## 3. CMMI practice areas → repository artifacts

- **Requirements Development & Management (RDM)** → `requirements/REQ.md` + `requirements/RTM.md`
- **Technical Solution (TS)** → `design/SDD.md` + `src/`
- **Decision Analysis & Resolution (DAR)** → `design/decision-log.md`
- **Verification & Validation (VV)** → `testbench/` (virtual test benches, mocks)
- **Measurement & Analysis (M&A)** → `performance/` (curves, KPIs, benchmarks)
- **Configuration Management (CM)** → Git versioning + immutable `docs/`
- **Process & Product Quality Assurance (PQA)** → review criteria in `assets/`
- **Risk & Opportunity Management (RSK)** → risk register in each project README
- **Planning & Estimating (EST/PLAN)** → scope and milestones in each project README
- **Peer Reviews (PR)** → review checklist in `assets/`

## 4. Mandatory artifacts per project

Every `projects/<project>/` folder must contain, at minimum:

```text
requirements/   REQ.md, RTM.md         (requirements + traceability matrix)
design/         SDD.md, decision-log.md (design + decision log)
testbench/      README.md (virtual test bench plan)
performance/    README.md (KPI measurement plan)
src/            technical sub-projects + one README.md per sub-project
README.md       project charter (scope, KPIs, risks, milestones)
```

## 5. "Build vs Reuse" rule (CBSE)

- **Reuse** an open-source component when it meets footprint and latency criteria and its
  protocol compliance is proven (e.g. `pymodbus`, Eclipse Mosquitto).
- **Build in-house** any component requiring strict "Fail-Fast" behavior, a proprietary data
  schema, or a CMMI L3 quality guarantee (e.g. protocol adapters, behavioral analysis engines).

Each choice is recorded in `design/decision-log.md` (criteria, options, decision, rationale).
