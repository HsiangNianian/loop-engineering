"""Built-in recovery policies."""

from loop_engineering.models import Action, Observation, RecoveryInstruction, Verification


class FeedbackRecovery:
    """Turn validator failures into bounded guidance for the next attempt."""

    def recover(
        self,
        *,
        observation: Observation,
        action: Action,
        verification: Verification,
        recovery_number: int,
    ) -> RecoveryInstruction:
        del observation, action
        return RecoveryInstruction(
            guidance=(
                f"Recovery {recovery_number}: revise the candidate using this verification "
                f"feedback: {verification.feedback}"
            )
        )
