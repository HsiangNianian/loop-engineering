"""Run one deterministic verification-recovery cycle."""

from loop_engineering import (
    BudgetLimits,
    CompositeVerifier,
    ContainsAllValidator,
    LoopEngine,
    NonEmptyValidator,
    ObjectiveObserver,
    ScriptedActor,
)


def main() -> None:
    engine = LoopEngine(
        observer=ObjectiveObserver(),
        actor=ScriptedActor(["Still drafting", "READY: checks passed"]),
        verifier=CompositeVerifier(
            [NonEmptyValidator(), ContainsAllValidator(required=("READY",))]
        ),
    )
    result = engine.run(
        "Produce a readiness decision containing READY",
        budget=BudgetLimits(max_iterations=3, max_actions=3, max_recoveries=2),
    )
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
