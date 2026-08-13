# Concepts

This directory will hold precise definitions, examples, and counterexamples for the Loop
Engineering vocabulary.

Initial invariants:

1. An iteration contains one observation, one action, and one verification.
2. Recovery is feedback for another bounded attempt, not permission to run forever.
3. A successful stop requires named evidence from validators.
4. Every terminal state has a machine-readable reason and usage counters.
5. A loop cannot grant itself more budget, authority, tools, or weaker acceptance criteria.

Planned notes include evidence contracts, retry ownership, stop-condition ordering, idempotency,
and the distinction between application recovery and harness-level fault recovery.
