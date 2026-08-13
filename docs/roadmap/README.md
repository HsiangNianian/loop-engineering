# Roadmap

Roadmap items are accepted only when they preserve bounded execution and add corresponding tests or
evaluation evidence.

## M0 — Executable foundation

Status: implemented.

- Synchronous observe-act-verify-recover/stop kernel.
- Immutable domain records and inspectable event trace.
- Iteration, action, and recovery limits.
- Deterministic validators, scripted actor, Responses API actor, and CLI.
- Offline unit tests and documented seven-layer boundary.

Acceptance gate: formatting, lint, tests, and scripted CLI smoke test pass without an API key.

## M1 — Reliability contracts

Status: planned.

- Add wall-clock, token, and monetary budgets.
- Define exception classes and retry ownership across Loop and Harness Engineering.
- Add cancellation, async components, checkpoints, and deterministic trace replay.
- Specify invariants with property-based tests.

Acceptance gate: injected actor, verifier, cancellation, and persistence faults all terminate within
declared limits and retain enough trace evidence to explain the result.

## M2 — Evidence and evaluation

Status: planned.

- Add schema, tool-result, test-suite, and human-approval validators.
- Publish task fixtures and loop-policy baselines under `evals/`.
- Measure success, false-pass rate, recovery efficiency, latency, and cost.

Acceptance gate: results are reproducible from versioned fixtures and traces; no aggregate score can
hide a constraint violation.

## M3 — Stack integration

Status: planned.

- Compile loop inputs from an Intent Engineering contract.
- Expose a Graph Engineering node adapter and isolated checkpoint boundary.
- Let Emergence Engineering tune policies only within immutable budget, evidence, and authority
  envelopes.

Acceptance gate: integration tests prove that adjacent layers cannot silently expand authority,
remove validators, or bypass terminal evidence.
