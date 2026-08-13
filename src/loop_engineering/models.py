"""Domain models shared by loop components."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Phase(StrEnum):
    """A visible phase in one loop execution."""

    OBSERVE = "observe"
    ACT = "act"
    VERIFY = "verify"
    RECOVER = "recover"
    STOP = "stop"


class LoopStatus(StrEnum):
    """Terminal status of a loop run."""

    SUCCEEDED = "succeeded"
    STOPPED = "stopped"


class ExitReason(StrEnum):
    """Machine-readable reason for stopping."""

    VERIFIED = "verified"
    ITERATION_BUDGET_EXHAUSTED = "iteration_budget_exhausted"
    ACTION_BUDGET_EXHAUSTED = "action_budget_exhausted"
    RECOVERY_BUDGET_EXHAUSTED = "recovery_budget_exhausted"


class BudgetLimits(BaseModel):
    """Hard limits that bound a loop run."""

    model_config = ConfigDict(frozen=True)

    max_iterations: int = Field(default=4, ge=1)
    max_actions: int = Field(default=4, ge=1)
    max_recoveries: int = Field(default=2, ge=0)


class BudgetUsage(BaseModel):
    """Counters consumed by a loop run."""

    model_config = ConfigDict(frozen=True)

    iterations: int = Field(default=0, ge=0)
    actions: int = Field(default=0, ge=0)
    recoveries: int = Field(default=0, ge=0)


class Observation(BaseModel):
    """The actor's task-local view at the start of an iteration."""

    model_config = ConfigDict(frozen=True)

    objective: str = Field(min_length=1)
    iteration: int = Field(ge=1)
    previous_output: str | None = None
    recovery_guidance: str | None = None


class Action(BaseModel):
    """A candidate output produced by an actor."""

    model_config = ConfigDict(frozen=True)

    content: str
    source: str = "actor"


class ValidatorResult(BaseModel):
    """Evidence emitted by one validator."""

    model_config = ConfigDict(frozen=True)

    validator: str
    passed: bool
    detail: str


class Verification(BaseModel):
    """Aggregate evidence for a candidate action."""

    model_config = ConfigDict(frozen=True)

    passed: bool
    results: tuple[ValidatorResult, ...]

    @property
    def feedback(self) -> str:
        failures = [result.detail for result in self.results if not result.passed]
        return "; ".join(failures) if failures else "All validators passed."


class RecoveryInstruction(BaseModel):
    """Feedback supplied to the next observation after verification fails."""

    model_config = ConfigDict(frozen=True)

    guidance: str = Field(min_length=1)


class LoopSnapshot(BaseModel):
    """Immutable state exposed to exit conditions."""

    model_config = ConfigDict(frozen=True)

    objective: str
    budget: BudgetLimits
    usage: BudgetUsage
    last_action: Action | None = None
    last_verification: Verification | None = None


class ExitDecision(BaseModel):
    """A terminal decision returned by an exit condition."""

    model_config = ConfigDict(frozen=True)

    status: LoopStatus
    reason: ExitReason
    detail: str


class LoopEvent(BaseModel):
    """One inspectable transition in the execution trace."""

    model_config = ConfigDict(frozen=True)

    phase: Phase
    iteration: int = Field(ge=0)
    detail: str


class LoopResult(BaseModel):
    """Terminal output and evidence from a loop run."""

    model_config = ConfigDict(frozen=True)

    objective: str
    status: LoopStatus
    reason: ExitReason
    detail: str
    final_output: str | None
    usage: BudgetUsage
    last_verification: Verification | None
    events: tuple[LoopEvent, ...]
