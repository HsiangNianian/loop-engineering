from dataclasses import dataclass, field

import httpx2
import pytest
from openai import OpenAI

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


@pytest.mark.parametrize(
    ("configured_baseurl", "expected_request_url"),
    [
        (None, "https://api.openai.com/v1/responses"),
        ("https://gateway.example/v1", "https://gateway.example/v1/responses"),
    ],
)
def test_actor_client_uses_configured_baseurl_without_network(
    configured_baseurl: str | None,
    expected_request_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request_urls: list[str] = []
    constructor_calls: list[dict[str, str | None]] = []

    def respond(request: httpx2.Request) -> httpx2.Response:
        request_urls.append(str(request.url))
        return httpx2.Response(
            200,
            json={
                "id": "resp_test",
                "created_at": 0,
                "model": "test-model",
                "object": "response",
                "output": [
                    {
                        "id": "msg_test",
                        "content": [{"annotations": [], "text": "READY", "type": "output_text"}],
                        "role": "assistant",
                        "status": "completed",
                        "type": "message",
                    }
                ],
                "parallel_tool_calls": False,
                "tool_choice": "auto",
                "tools": [],
            },
            request=request,
        )

    with httpx2.Client(transport=httpx2.MockTransport(respond)) as http_client:

        def build_client(*, api_key: str, base_url: str | None) -> OpenAI:
            constructor_calls.append({"api_key": api_key, "base_url": base_url})
            return OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)

        monkeypatch.setattr("loop_engineering.actors.OpenAI", build_client)
        actor = OpenAIResponsesActor(
            Settings(
                _env_file=None,
                openai_api_key="test-secret",
                openai_model="test-model",
                openai_baseurl=configured_baseurl,
            )
        )
        action = actor.act(Observation(objective="Return READY", iteration=1))

    assert action.content == "READY"
    assert constructor_calls == [{"api_key": "test-secret", "base_url": configured_baseurl}]
    assert request_urls == [expected_request_url]
