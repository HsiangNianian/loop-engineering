from loop_engineering import (
    BudgetLimits,
    CompositeVerifier,
    ContainsAllValidator,
    ExitReason,
    LoopEngine,
    LoopStatus,
    NonEmptyValidator,
    ObjectiveObserver,
    Phase,
    ScriptedActor,
)


def make_engine(actions: list[str]) -> LoopEngine:
    return LoopEngine(
        observer=ObjectiveObserver(),
        actor=ScriptedActor(actions),
        verifier=CompositeVerifier(
            [NonEmptyValidator(), ContainsAllValidator(required=("READY",))]
        ),
    )


def test_loop_succeeds_with_validator_evidence() -> None:
    result = make_engine(["READY"]).run("Make a readiness decision")

    assert result.status is LoopStatus.SUCCEEDED
    assert result.reason is ExitReason.VERIFIED
    assert result.final_output == "READY"
    assert result.usage.iterations == 1
    assert result.usage.actions == 1
    assert result.usage.recoveries == 0
    assert result.last_verification is not None
    assert result.last_verification.passed
    assert [event.phase for event in result.events] == [
        Phase.OBSERVE,
        Phase.ACT,
        Phase.VERIFY,
        Phase.STOP,
    ]


def test_failed_verification_is_recovered_into_next_observation() -> None:
    result = make_engine(["not finished", "READY after feedback"]).run("Make a readiness decision")

    assert result.status is LoopStatus.SUCCEEDED
    assert result.usage.iterations == 2
    assert result.usage.recoveries == 1
    assert "Missing required markers" in result.events[2].detail
    assert result.events[3].phase is Phase.RECOVER
    assert "Recovery 1" in result.events[3].detail


def test_two_recoveries_allow_a_third_attempt() -> None:
    result = make_engine(["draft one", "draft two", "READY after two recoveries"]).run(
        "Make a readiness decision",
        budget=BudgetLimits(max_iterations=3, max_actions=3, max_recoveries=2),
    )

    assert result.status is LoopStatus.SUCCEEDED
    assert result.reason is ExitReason.VERIFIED
    assert result.usage.iterations == 3
    assert result.usage.actions == 3
    assert result.usage.recoveries == 2
    assert [event.phase for event in result.events].count(Phase.RECOVER) == 2


def test_recovery_budget_stops_a_persistently_failing_loop() -> None:
    result = make_engine(["unfinished"]).run(
        "Make a readiness decision",
        budget=BudgetLimits(max_iterations=4, max_actions=4, max_recoveries=0),
    )

    assert result.status is LoopStatus.STOPPED
    assert result.reason is ExitReason.RECOVERY_BUDGET_EXHAUSTED
    assert result.usage.recoveries == 0
    assert result.usage.iterations == 1


def test_success_on_last_iteration_wins_over_budget_exhaustion() -> None:
    result = make_engine(["READY"]).run(
        "Make a readiness decision",
        budget=BudgetLimits(max_iterations=1, max_actions=1, max_recoveries=0),
    )

    assert result.status is LoopStatus.SUCCEEDED
    assert result.reason is ExitReason.VERIFIED
