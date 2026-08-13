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
