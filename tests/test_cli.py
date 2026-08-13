import json

from loop_engineering.cli import main


def test_cli_runs_scripted_loop_without_api_key(capsys, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    exit_code = main(
        [
            "run",
            "Produce readiness evidence",
            "--require",
            "READY",
            "--scripted-action",
            "draft",
            "--scripted-action",
            "READY",
            "--json",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["status"] == "succeeded"
    assert payload["usage"]["recoveries"] == 1
