# Loop Engineering

Loop Engineering is a research and learning repository about reliable agent feedback loops. It
serves people learning agent systems and developers testing loop policies at the frontier.

The code is an executable research and reference prototype. It makes the ideas inspectable and
testable; it is not presented as a production agent framework.

> **Status:** experimental foundation. The synchronous reference path works and is tested offline.
> Roadmap items describe planned research, not shipped features.

## Why study the loop?

A model call produces a candidate. A loop decides what the model sees next, what counts as progress,
how failure changes the next attempt, and when further work is no longer justified.

Repetition alone is not reliability. A bounded agent loop needs named evidence, explicit resource
limits, recovery policy, and a machine-readable reason for stopping.

This repository studies one compact transition system:

```text
observe -> act -> verify -> recover or stop
```

Each transition is a replaceable protocol. Each run returns its output, validator evidence, budget
usage, terminal reason, and event trace.

## Who this is for

- **Agent newcomers** who want a small system they can read before approaching orchestration
  frameworks.
- **Agent builders** who need explicit loop contracts instead of an unbounded `while` around model
  calls.
- **Frontier developers and researchers** who want to test recovery, verification, budgeting, and
  termination policies against reproducible traces.

Prior agent-framework experience is not required. The implementation assumes basic Python and
command-line familiarity.

## Choose a path

### Learn

Start with the five [concept invariants](docs/concepts/README.md), then run the deterministic example
in [Quickstart](#quickstart). Read its JSON trace alongside `LoopEngine.run` to connect terms to state
transitions.

Next, change a scripted action or required marker and predict the terminal reason before rerunning
the command. The tests provide short examples of boundary behavior.

### Build

Use the protocols in `ports.py` to supply an observer, actor, verifier, recovery strategy, or exit
condition. Keep external model and tool clients at the edge of the engine.

Begin with deterministic actors and validators. Add live OpenAI calls only after the local evidence
and budget contract behaves as intended.

### Research

Choose an [open research question](#open-research-questions), state a falsifiable hypothesis, and put
disposable work under `experiments/`. Record budgets, policy variants, model settings, and raw traces.

Move reusable tasks and metrics into `evals/`. Promote behavior into `src/` only when its contract and
regression tests are clear.

## Scope

This repository owns the mechanics and semantics of one bounded feedback loop:

- the `observe -> act -> verify -> recover/stop` transition;
- iteration, action, and recovery budgets;
- evidence-producing validators rather than model self-confidence;
- pluggable observers, actors, verifiers, recovery strategies, and exit conditions;
- terminal results with evidence, resource usage, trace events, and a stop reason;
- an OpenAI Responses API actor and a deterministic actor for learning and evaluation.

The implementation stays small enough to inspect in one sitting. Its job is to make loop policy
executable before adding concurrency, persistence, tools, or orchestration.

## Non-goals

Loop Engineering does **not** currently provide:

- prompt libraries or prompt optimization;
- retrieval, memory, or context-window management;
- tool sandboxes, permissions, durable checkpoints, or transport retry policy;
- multi-agent routing or workflow graph execution;
- dynamic role creation or topology mutation;
- automatic inference of human values, authority, or success criteria;
- proof that arbitrary model output is correct without external validation.

Those concerns belong to adjacent layers. A clear boundary keeps an impressive demo from hiding
missing evidence, authority, or resource limits.

## Boundary in the seven-layer stack

| Layer | Engineering object | Relationship to this repository |
| --- | --- | --- |
| Prompt Engineering | How instructions shape model behavior | Supplies actor instructions; does not own loop control. |
| Context Engineering | What an agent sees, remembers, retrieves, and forgets | Supplies observations; this prototype passes task-local state. |
| Harness Engineering | Tools, permissions, execution, runtime recovery, and observability | Hosts loops and owns infrastructure failures outside verification. |
| **Loop Engineering** | How one agent iterates, proves progress, recovers, and stops | **Owned here.** |
| Graph Engineering | How multiple loops coordinate through state and routing | Composes loops as nodes without replacing their local contracts. |
| Emergence Engineering | How roles and topology adapt under bounded rules | May tune loops but must preserve their budgets and evidence contracts. |
| Intent Engineering | How goals, constraints, authority, and success evidence become executable | Compiles objectives, validators, budgets, and allowed recovery policy. |

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

The actor calls `client.responses.create(...)` through `openai-python`. Verification stays local and
deterministic: this candidate must be non-empty and contain `READY`.

Run the same feedback structure without a key or network request:

```bash
uv run loop-engineering run \
  "Produce a readiness decision" \
  --require READY \
  --scripted-action "Needs revision" \
  --scripted-action "READY" \
  --json
```

The first candidate fails. Its evidence becomes recovery guidance, the second candidate passes, and
the trace ends with `reason: "verified"`.

Run the repository checks:

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
uv build
```

## Configuration

`pydantic-settings` loads process variables and an optional local `.env` file. Process variables take
precedence, and `.env` is ignored by Git.

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | For live calls | none | Credential passed to the OpenAI client. |
| `OPENAI_MODEL` | No | `gpt-5.6` | Model passed to the Responses API. |
| `OPENAI_BASEURL` | No | none | Base URL for an OpenAI-compatible Responses API. |

The custom endpoint variable is spelled exactly `OPENAI_BASEURL`. An unset, empty, or whitespace-only
value becomes `None`, so the OpenAI SDK keeps its default endpoint.

```dotenv
OPENAI_BASEURL=https://gateway.example.com/v1
```

The client appends the Responses API resource path. A custom service must implement the contract used
by the installed `openai-python` version.

CLI budgets are hard limits:

| Flag | Default | Meaning |
| --- | ---: | --- |
| `--max-iterations` | `4` | Maximum observe cycles. |
| `--max-actions` | `4` | Maximum actor invocations. |
| `--max-recoveries` | `2` | Failed attempts allowed to feed another attempt. |

`--require TEXT` is repeatable. `--scripted-action TEXT` is also repeatable and replaces the live
actor, which makes examples and CI reproducible.

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

One iteration has one observation, one action, and one verification. Failed verification may produce
one recovery instruction for the next observation.

Exit conditions run before work begins and after evidence is produced. Verification precedes budget
checks, so a candidate that succeeds on its final permitted attempt still succeeds.

The OpenAI adapter sits at the edge. `LoopEngine` imports no OpenAI types and accepts any synchronous
actor that satisfies the protocol.

Validators retain individual results. A passing aggregate therefore has inspectable evidence rather
than a boolean without provenance.

## Open research questions

These are working questions, not claims that the prototype has solved them.

### How can verification avoid circularity?

When actor and verifier share a model or data source, correlated errors can create false confidence.
What evidence mix reduces false passes without making every task prohibitively expensive?

### When does recovery become thrashing?

Repeated feedback may refine a candidate or trap it in a local strategy. Which trace signals should
trigger another revision, a strategy change, escalation, or an early stop?

### How should budgets move between attempts?

Fixed limits are simple but may spend too much on weak paths or too little near success. Can a policy
allocate time, tokens, and cost by expected evidence gain while preserving hard ceilings?

### How should conflicting evidence terminate a loop?

Validators may disagree, arrive late, or have different authority. What composition rules preserve
safety while allowing partial success and explicit human approval?

### Which comparisons survive stochastic models?

Model versions and environments drift. What trace schema, task fixtures, and replay boundaries let us
compare loop policies without confusing policy quality with model or infrastructure changes?

## Repository tree

```text
.
├── docs/
│   ├── README.md              # documentation map
│   ├── concepts/README.md     # vocabulary and invariants
│   └── roadmap/README.md      # staged research roadmap
├── evals/README.md            # planned evaluation suites and metrics
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

The placeholder directories are deliberate. New work should state its contract and evaluation plan
before it expands the reference implementation.

## Roadmap

### Foundation — current

- [x] Typed observe-act-verify-recover/stop domain model.
- [x] Explicit iteration, action, and recovery budgets.
- [x] Composable validators and machine-readable exit reasons.
- [x] OpenAI Responses API adapter with `.env` configuration.
- [x] Offline deterministic actor, CLI, examples, and tests.

### Reliability — next

- [ ] Async cancellation and wall-clock, token, and cost budgets.
- [ ] Structured-output actions and schema validators.
- [ ] Durable checkpoints and resumable event logs through harness adapters.
- [ ] Exception classification with explicit retry ownership.
- [ ] Property-based tests for transition and budget invariants.

### Measurement

- [ ] Versioned task fixtures, fault injection, and baseline policies.
- [ ] Success, cost, latency, recovery-efficiency, and false-pass metrics.
- [ ] Trace replay and policy comparison without another model call.

### Integration

- [ ] Intent-contract compiler input.
- [ ] Graph-node adapter with isolated state and failure boundaries.
- [ ] Emergence-safe hooks that cannot relax evidence or authority constraints.

See [docs/roadmap/README.md](docs/roadmap/README.md) for milestone acceptance gates.

## Status and guarantees

The synchronous reference path currently provides deterministic budget accounting, explicit terminal
reasons, and offline-testable policy composition.

It does not guarantee arbitrary model output. A result is only as trustworthy as its validators and
their evidence. Live OpenAI calls require user credentials and are not part of the offline test suite.

This is an early research prototype. APIs may change as its vocabulary, invariants, and evaluations
become sharper.

## License

[MIT](LICENSE)
