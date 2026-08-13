"""Synchronous reference engine for a bounded agent feedback loop."""

from dataclasses import dataclass, field

from loop_engineering.conditions import BudgetExitCondition, VerifiedExitCondition
from loop_engineering.models import (
    Action,
    BudgetLimits,
    BudgetUsage,
    ExitDecision,
    LoopEvent,
    LoopResult,
    LoopSnapshot,
    Phase,
    RecoveryInstruction,
    Verification,
)
from loop_engineering.ports import (
    Actor,
    ExitCondition,
    Observer,
    RecoveryStrategy,
    Verifier,
)
from loop_engineering.recovery import FeedbackRecovery


@dataclass(slots=True)
class LoopEngine:
    """Run observe -> act -> verify -> recover/stop under explicit budgets."""

    observer: Observer
    actor: Actor
    verifier: Verifier
    recovery_strategy: RecoveryStrategy = field(default_factory=FeedbackRecovery)
    exit_conditions: tuple[ExitCondition, ...] = field(
        default_factory=lambda: (VerifiedExitCondition(), BudgetExitCondition())
    )

    def run(self, objective: str, *, budget: BudgetLimits | None = None) -> LoopResult:
        objective = objective.strip()
        if not objective:
            raise ValueError("objective must not be empty")

        limits = budget or BudgetLimits()
        usage = BudgetUsage()
        events: list[LoopEvent] = []
        previous_action: Action | None = None
        last_verification: Verification | None = None
        recovery: RecoveryInstruction | None = None

        while True:
            snapshot = LoopSnapshot(
                objective=objective,
                budget=limits,
                usage=usage,
                last_action=previous_action,
                last_verification=last_verification,
            )
            if decision := self._exit_decision(snapshot):
                return self._result(snapshot, decision, events)

            iteration = usage.iterations + 1
            observation = self.observer.observe(
                objective=objective,
                iteration=iteration,
                previous_action=previous_action,
                recovery=recovery,
            )
            usage = usage.model_copy(update={"iterations": iteration})
            events.append(LoopEvent(phase=Phase.OBSERVE, iteration=iteration, detail="Observed."))

            previous_action = self.actor.act(observation)
            usage = usage.model_copy(update={"actions": usage.actions + 1})
            events.append(
                LoopEvent(
                    phase=Phase.ACT,
                    iteration=iteration,
                    detail=f"Produced action via {previous_action.source}.",
                )
            )

            last_verification = self.verifier.verify(previous_action, observation)
            events.append(
                LoopEvent(
                    phase=Phase.VERIFY,
                    iteration=iteration,
                    detail=last_verification.feedback,
                )
            )

            snapshot = LoopSnapshot(
                objective=objective,
                budget=limits,
                usage=usage,
                last_action=previous_action,
                last_verification=last_verification,
            )
            if decision := self._exit_decision(snapshot):
                return self._result(snapshot, decision, events)

            recovery_number = usage.recoveries + 1
            recovery = self.recovery_strategy.recover(
                observation=observation,
                action=previous_action,
                verification=last_verification,
                recovery_number=recovery_number,
            )
            usage = usage.model_copy(update={"recoveries": recovery_number})
            events.append(
                LoopEvent(
                    phase=Phase.RECOVER,
                    iteration=iteration,
                    detail=recovery.guidance,
                )
            )
            # The failed verification has now been handled. Clearing it prevents the next
            # pre-flight budget check from stopping before the paid-for recovery can be used.
            last_verification = None

    def _exit_decision(self, snapshot: LoopSnapshot) -> ExitDecision | None:
        for condition in self.exit_conditions:
            if decision := condition.evaluate(snapshot):
                return decision
        return None

    @staticmethod
    def _result(
        snapshot: LoopSnapshot,
        decision: ExitDecision,
        events: list[LoopEvent],
    ) -> LoopResult:
        stop_iteration = snapshot.usage.iterations
        events.append(LoopEvent(phase=Phase.STOP, iteration=stop_iteration, detail=decision.detail))
        return LoopResult(
            objective=snapshot.objective,
            status=decision.status,
            reason=decision.reason,
            detail=decision.detail,
            final_output=snapshot.last_action.content if snapshot.last_action else None,
            usage=snapshot.usage,
            last_verification=snapshot.last_verification,
            events=tuple(events),
        )
