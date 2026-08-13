# Loop Engineering

Reliable agent feedback loops with explicit evidence, budgets, recovery, and stop conditions.

Loop Engineering treats persistence as an engineering object. A model call is not a loop, and
repetition is not reliability. A useful loop must observe the current task-local state, produce a
candidate action, verify it against named evidence, recover from a failed attempt, and stop for a
machine-readable reason before it consumes unbounded resources.

This repository is the executable reference for that idea in the broader Agent Engineering Stack.
It contains a small synchronous Python kernel, an OpenAI Responses API actor, deterministic actors
for evaluation, composable validators, hard budgets, trace events, and a CLI.

> **Status:** experimental foundation. The reference path works and is tested offline; the roadmap
> directories describe planned research rather than shipped features.

## Scope

This repository owns the mechanics and semantics of a single bounded feedback loop:

- the `observe -> act -> verify -> recover/stop` state transition;
- explicit iteration, action, and recovery budgets;
- evidence-producing validators instead of model self-confidence;
- pluggable observers, actors, verifiers, recovery strategies, and exit conditions;
- a terminal result with a reason, final evidence, resource usage, and event trace;
- one production-facing OpenAI Responses API adapter and one deterministic test adapter.

The current implementation is deliberately small enough to inspect in one sitting. Its purpose is
to make loop policy testable before adding concurrency, persistence, tools, or orchestration.

## Non-goals

Loop Engineering does **not** currently attempt to provide:

- prompt libraries or prompt optimization;
- retrieval, memory, or context-window management;
- tool sandboxes, permissions, durable checkpoints, or transport retry policy;
- multi-agent routing or workflow graph execution;
- dynamic role creation or topology mutation;
- automatic inference of human values, authority, or success criteria;
- a claim that model-generated output is correct without external validation.

Those concerns belong to adjacent layers. Keeping the boundary visible prevents an impressive demo
from hiding missing evidence or unbounded execution.

## Boundary in the seven-layer stack

| Layer | Engineering object | Relationship to this repository |
| --- | --- | --- |
| Prompt Engineering | How an instruction shapes model behavior | Supplies an actor's instruction; does not own loop control. |
| Context Engineering | What an agent sees, remembers, retrieves, and forgets | Supplies observations; this loop only passes task-local state. |
| Harness Engineering | Tools, permissions, execution, recovery infrastructure, and observability | Hosts the loop and handles runtime/tool failures outside application verification. |
| **Loop Engineering** | How one agent iterates, proves progress, recovers, and stops | **Owned here.** |
| Graph Engineering | How multiple loops coordinate through state, routing, and failure boundaries | Composes loop instances as nodes; does not replace their local contracts. |
| Emergence Engineering | How roles and topology adapt under bounded rules | May create or tune loops, but must preserve their budgets and evidence contracts. |
| Intent Engineering | How goals, constraints, trade-offs, authority, and success evidence become executable | Compiles the objective, validators, budgets, and allowed recovery policy. |

## Quickstart

Requirements: Python 3.12 or newer and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env
```

Add an API key to `.env`, then run a live loop:

```bash
uv run loop-engineering run \
  "Return a concise release decision containing READY" \
  --require READY
```

The actor calls `client.responses.create(...)` through `openai-python`. Verification remains local
and deterministic: in this example the candidate must be non-empty and contain `READY`.

Run the complete loop without an API key or network request:

```bash
uv run loop-engineering run \
  "Produce a readiness decision" \
  --require READY \
  --scripted-action "Needs revision" \
  --scripted-action "READY" \
  --json
```

The first candidate fails verification, feedback becomes recovery guidance, the second candidate
passes, and the JSON trace ends with `reason: "verified"`.

Useful development commands:

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
```

## Configuration

Configuration is loaded by `pydantic-settings` from environment variables and an optional local
`.env` file. Process environment variables take precedence. `.env` is ignored by Git.

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | For live calls | none | Credential passed to the OpenAI client. |
| `OPENAI_MODEL` | No | `gpt-5.6` | Model passed to the Responses API. |

CLI budgets are hard limits:

| Flag | Default | Meaning |
| --- | ---: | --- |
| `--max-iterations` | `4` | Maximum observe cycles. |
| `--max-actions` | `4` | Maximum actor invocations. |
| `--max-recoveries` | `2` | Maximum failed attempts allowed to feed another attempt. |

`--require TEXT` is repeatable. `--scripted-action TEXT` is also repeatable and replaces the live
OpenAI actor, which makes experiments and CI reproducible.

## Architecture

The engine depends on five small protocols:

```text
                     hard BudgetLimits
                            |
                            v
Objective -> Observer -> Observation -> Actor -> Action
                                        ^          |
                                        |          v
                                  Recovery <- Verifier
                                        |       |
                                        +-------+
                                     failed evidence

VerifiedExitCondition -----------> success + stop event
BudgetExitCondition -------------> bounded stop event
```

One iteration has exactly one observation, one action, and one verification. A failed verification
can produce one recovery instruction for the next observation. Exit conditions are checked before
work begins and immediately after evidence is produced. The verified condition runs before budget
conditions, so a candidate that succeeds on its final permitted attempt is still successful.

The OpenAI adapter is intentionally at the edge. `LoopEngine` imports no OpenAI types and can run
with any synchronous actor satisfying the protocol. Validators retain individual results so a
passing aggregate is backed by inspectable evidence rather than a boolean with no provenance.

## Repository tree

```text
.
├── docs/
│   ├── README.md              # documentation map
│   ├── concepts/README.md     # vocabulary and invariants placeholder
│   └── roadmap/README.md      # staged implementation roadmap
├── evals/README.md            # evaluation suites and metrics placeholder
├── examples/
│   ├── README.md              # runnable example index
│   └── basic.py               # deterministic recovery example
├── experiments/README.md      # research protocol placeholder
├── src/loop_engineering/
│   ├── actors.py              # OpenAI Responses and scripted actors
│   ├── cli.py                 # command-line entry point
│   ├── conditions.py          # verified and budget exit policies
│   ├── engine.py              # reference state machine
│   ├── models.py              # immutable domain contracts
│   ├── observers.py           # task-local observation policy
│   ├── ports.py               # component protocols
│   ├── recovery.py            # validator-feedback recovery
│   ├── settings.py            # .env-backed settings
│   └── validators.py          # evidence-producing validators
└── tests/                     # offline unit and CLI tests
```

The placeholder directories are intentional roadmap surfaces: future work should first state its
contract and evaluation plan there, then add implementation code.

## Roadmap

### Foundation — current

- [x] Typed observe-act-verify-recover/stop domain model.
- [x] Explicit iteration, action, and recovery budgets.
- [x] Composable validators and machine-readable exit reasons.
- [x] OpenAI Responses API adapter with `.env` configuration.
- [x] Offline deterministic actor, CLI, and tests.

### Reliability — next

- [ ] Async cancellation and wall-clock/token/cost budgets.
- [ ] Structured-output actions and schema validators.
- [ ] Durable checkpoints and resumable event logs through harness adapters.
- [ ] Exception classification with explicit retry ownership.
- [ ] Property-based tests for transition and budget invariants.

### Measurement

- [ ] Standard task fixtures, fault injection, and baseline policies.
- [ ] Success, cost, latency, recovery-efficiency, and false-pass metrics.
- [ ] Trace replay and policy comparison without another model call.

### Integration

- [ ] Intent-contract compiler input.
- [ ] Graph-node adapter with isolated state and failure boundaries.
- [ ] Emergence-safe policy hooks that cannot relax evidence or authority constraints.

See [docs/roadmap/README.md](docs/roadmap/README.md) for milestones and acceptance gates.

## Status and guarantees

The repository currently guarantees deterministic budget accounting, explicit terminal reasons,
and offline-testable policy composition for the synchronous reference path. It does not guarantee
the correctness of arbitrary model output; correctness is only as strong as the configured
validators. The live OpenAI path requires user-provided credentials and is not exercised in tests.

This is an early experimental project. APIs may change while the vocabulary, invariants, and evals
are being established.

## License

[MIT](LICENSE)
