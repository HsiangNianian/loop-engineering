from dataclasses import dataclass, field

from loop_engineering.actors import OpenAIResponsesActor
from loop_engineering.models import Observation
from loop_engineering.settings import Settings


@dataclass
class FakeResponse:
    output_text: str


@dataclass
class FakeResponses:
    calls: list[dict[str, object]] = field(default_factory=list)

    def create(self, *, model: str, input: list[dict[str, str]]) -> FakeResponse:
        self.calls.append({"model": model, "input": input})
        return FakeResponse(output_text="  READY  ")


@dataclass
class FakeClient:
    responses: FakeResponses = field(default_factory=FakeResponses)


def test_openai_actor_uses_responses_api_without_network() -> None:
    client = FakeClient()
    actor = OpenAIResponsesActor(Settings(openai_model="test-model"), client=client)

    action = actor.act(
        Observation(
            objective="Make a decision",
            iteration=2,
            previous_output="draft",
            recovery_guidance="Include READY",
        )
    )

    assert action.content == "READY"
    assert action.source == "openai.responses"
    assert client.responses.calls[0]["model"] == "test-model"
    messages = client.responses.calls[0]["input"]
    assert isinstance(messages, list)
    assert "Include READY" in messages[1]["content"]
