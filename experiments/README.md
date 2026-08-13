# Experiments

This directory is reserved for hypotheses and disposable research code about loop policies.

Every experiment should record:

- the hypothesis and policy variants;
- fixed task and model inputs;
- budget and validator configuration;
- random seeds or sampling controls where available;
- raw trace locations and a falsifiable success criterion;
- observed failures, including false-positive verification.

An experiment is not a shipped feature. Reusable fixtures move to `evals/`; stable behavior moves to
`src/` only after its contract and regression tests are clear.
