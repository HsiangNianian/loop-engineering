# Evaluations

This directory will contain versioned tasks and evaluation runners for comparing loop policies.

Planned metrics include:

- externally verified task success and false-pass rate;
- iterations, actions, recoveries, tokens, cost, and latency;
- recovery efficiency after injected failures;
- stop-reason accuracy and budget violations;
- reproducibility from a stored trace.

No current benchmark result is claimed. Evaluation fixtures must run offline when possible, and live
model evaluations must identify the model, configuration, date, and cost separately from deterministic
unit tests.
