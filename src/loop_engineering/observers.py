"""Built-in observation policies."""

from loop_engineering.models import Action, Observation, RecoveryInstruction


class ObjectiveObserver:
    """Expose only the objective and the previous feedback cycle to the actor."""

    def observe(
        self,
        *,
        objective: str,
        iteration: int,
        previous_action: Action | None,
        recovery: RecoveryInstruction | None,
    ) -> Observation:
        return Observation(
            objective=objective,
            iteration=iteration,
            previous_output=previous_action.content if previous_action else None,
            recovery_guidance=recovery.guidance if recovery else None,
        )
