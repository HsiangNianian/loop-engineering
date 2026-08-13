"""Standard exit conditions."""

from loop_engineering.models import (
    ExitDecision,
    ExitReason,
    LoopSnapshot,
    LoopStatus,
)


class VerifiedExitCondition:
    """Stop successfully once evidence says the objective is satisfied."""

    def evaluate(self, snapshot: LoopSnapshot) -> ExitDecision | None:
        if snapshot.last_verification and snapshot.last_verification.passed:
            return ExitDecision(
                status=LoopStatus.SUCCEEDED,
                reason=ExitReason.VERIFIED,
                detail="The candidate passed every validator.",
            )
        return None


class BudgetExitCondition:
    """Stop a failing loop before it can exceed a configured hard limit."""

    def evaluate(self, snapshot: LoopSnapshot) -> ExitDecision | None:
        if snapshot.usage.iterations >= snapshot.budget.max_iterations:
            return ExitDecision(
                status=LoopStatus.STOPPED,
                reason=ExitReason.ITERATION_BUDGET_EXHAUSTED,
                detail="The iteration budget was exhausted before verification succeeded.",
            )
        if snapshot.usage.actions >= snapshot.budget.max_actions:
            return ExitDecision(
                status=LoopStatus.STOPPED,
                reason=ExitReason.ACTION_BUDGET_EXHAUSTED,
                detail="The action budget was exhausted before verification succeeded.",
            )
        if (
            snapshot.last_verification
            and not snapshot.last_verification.passed
            and snapshot.usage.recoveries >= snapshot.budget.max_recoveries
        ):
            return ExitDecision(
                status=LoopStatus.STOPPED,
                reason=ExitReason.RECOVERY_BUDGET_EXHAUSTED,
                detail="The recovery budget was exhausted before verification succeeded.",
            )
        return None
