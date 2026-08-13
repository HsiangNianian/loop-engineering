from pathlib import Path

import pytest

from loop_engineering.settings import Settings


def test_settings_reads_named_environment_variables(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    settings = Settings()

    assert settings.require_api_key() == "test-secret"
    assert settings.openai_model == "test-model"


def test_default_model_is_gpt_5_6(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    assert Settings().openai_model == "gpt-5.6"


def test_settings_reads_exact_baseurl_name_from_dotenv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("OPENAI_BASEURL", raising=False)
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "OPENAI_API_KEY=dotenv-secret\n"
        "OPENAI_MODEL=dotenv-model\n"
        "OPENAI_BASEURL=https://gateway.example/v1\n",
        encoding="utf-8",
    )

    settings = Settings(_env_file=dotenv)

    assert settings.require_api_key() == "dotenv-secret"
    assert settings.openai_model == "dotenv-model"
    assert settings.openai_baseurl == "https://gateway.example/v1"


@pytest.mark.parametrize("value", [None, "", "   ", "\t\n"])
def test_blank_baseurl_is_normalized_to_none(value: str | None) -> None:
    assert Settings(_env_file=None, openai_baseurl=value).openai_baseurl is None
