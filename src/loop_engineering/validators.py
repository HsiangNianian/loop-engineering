"""Composable validators and aggregate verification."""

from dataclasses import dataclass
from typing import Protocol

from loop_engineering.models import Action, Observation, ValidatorResult, Verification


class Validator(Protocol):
    name: str

    def validate(self, action: Action, observation: Observation) -> ValidatorResult: ...


@dataclass(frozen=True, slots=True)
class NonEmptyValidator:
    """Require a candidate containing at least one non-whitespace character."""

    name: str = "non_empty"

    def validate(self, action: Action, observation: Observation) -> ValidatorResult:
        del observation
        passed = bool(action.content.strip())
        return ValidatorResult(
            validator=self.name,
            passed=passed,
            detail="Output is non-empty." if passed else "Output must not be empty.",
        )


@dataclass(frozen=True, slots=True)
class ContainsAllValidator:
    """Require literal evidence markers in the candidate output."""

    required: tuple[str, ...]
    case_sensitive: bool = False
    name: str = "contains_all"

    def validate(self, action: Action, observation: Observation) -> ValidatorResult:
        del observation
        haystack = action.content if self.case_sensitive else action.content.casefold()
        missing = [
            item
            for item in self.required
            if (item if self.case_sensitive else item.casefold()) not in haystack
        ]
        passed = not missing
        detail = (
            "All required markers are present."
            if passed
            else f"Missing required markers: {', '.join(missing)}."
        )
        return ValidatorResult(validator=self.name, passed=passed, detail=detail)


class CompositeVerifier:
    """Run every validator and retain its evidence."""

    def __init__(self, validators: list[Validator] | tuple[Validator, ...]) -> None:
        if not validators:
            raise ValueError("at least one validator is required")
        self._validators = tuple(validators)

    def verify(self, action: Action, observation: Observation) -> Verification:
        results = tuple(validator.validate(action, observation) for validator in self._validators)
        return Verification(passed=all(result.passed for result in results), results=results)
