"""Protocols that keep the loop independent from models, tools, and runtimes."""

from typing import Protocol

from loop_engineering.models import (
    Action,
    ExitDecision,
    LoopSnapshot,
    Observation,
    RecoveryInstruction,
    Verification,
)


class Observer(Protocol):
    def observe(
        self,
        *,
        objective: str,
        iteration: int,
        previous_action: Action | None,
        recovery: RecoveryInstruction | None,
    ) -> Observation: ...


class Actor(Protocol):
    def act(self, observation: Observation) -> Action: ...


class Verifier(Protocol):
    def verify(self, action: Action, observation: Observation) -> Verification: ...


class RecoveryStrategy(Protocol):
    def recover(
        self,
        *,
        observation: Observation,
        action: Action,
        verification: Verification,
        recovery_number: int,
    ) -> RecoveryInstruction: ...


class ExitCondition(Protocol):
    def evaluate(self, snapshot: LoopSnapshot) -> ExitDecision | None: ...
