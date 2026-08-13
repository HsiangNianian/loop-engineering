"""Actor adapters for deterministic tests and the OpenAI Responses API."""

from collections.abc import Iterable
from typing import Protocol

from openai import OpenAI

from loop_engineering.models import Action, Observation
from loop_engineering.settings import Settings


class ResponseLike(Protocol):
    output_text: str


class ResponsesResource(Protocol):
    def create(self, *, model: str, input: list[dict[str, str]]) -> ResponseLike: ...


class OpenAIClient(Protocol):
    responses: ResponsesResource


class OpenAIResponsesActor:
    """Generate candidate actions with the OpenAI Responses API."""

    def __init__(self, settings: Settings, client: OpenAIClient | None = None) -> None:
        self._settings = settings
        self._client = client or OpenAI(
            api_key=settings.require_api_key(),
            base_url=settings.openai_baseurl,
        )

    def act(self, observation: Observation) -> Action:
        feedback = observation.recovery_guidance or "No prior verification feedback."
        previous = observation.previous_output or "No prior candidate."
        response = self._client.responses.create(
            model=self._settings.openai_model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are the action step in a bounded engineering loop. Produce one "
                        "candidate that directly satisfies the objective. Use verification "
                        "feedback when present. Return only the candidate, without commentary."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Objective: {observation.objective}\n"
                        f"Iteration: {observation.iteration}\n"
                        f"Previous candidate: {previous}\n"
                        f"Recovery guidance: {feedback}"
                    ),
                },
            ],
        )
        return Action(content=response.output_text.strip(), source="openai.responses")


class ScriptedActor:
    """Replay deterministic actions for examples, tests, and evaluations."""

    def __init__(self, actions: Iterable[str]) -> None:
        self._actions = iter(actions)

    def act(self, observation: Observation) -> Action:
        del observation
        try:
            content = next(self._actions)
        except StopIteration as error:
            raise RuntimeError("scripted actor has no actions left") from error
        return Action(content=content, source="scripted")
