"""Command-line interface for the reference loop."""

import argparse
from collections.abc import Sequence

from loop_engineering.actors import OpenAIResponsesActor, ScriptedActor
from loop_engineering.engine import LoopEngine
from loop_engineering.models import BudgetLimits, LoopResult, LoopStatus
from loop_engineering.observers import ObjectiveObserver
from loop_engineering.settings import Settings
from loop_engineering.validators import CompositeVerifier, ContainsAllValidator, NonEmptyValidator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="loop-engineering",
        description="Run a bounded observe-act-verify-recover loop.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="run one bounded loop")
    run.add_argument("objective", help="the outcome the loop should produce")
    run.add_argument(
        "--require",
        action="append",
        default=[],
        metavar="TEXT",
        help="literal evidence required in the output; repeatable",
    )
    run.add_argument("--max-iterations", type=int, default=4)
    run.add_argument("--max-actions", type=int, default=4)
    run.add_argument("--max-recoveries", type=int, default=2)
    run.add_argument("--model", help="override OPENAI_MODEL")
    run.add_argument(
        "--scripted-action",
        action="append",
        metavar="TEXT",
        help="use deterministic actions instead of OpenAI; repeatable",
    )
    run.add_argument("--json", action="store_true", help="print the complete result as JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    settings = Settings()
    if args.model:
        settings = settings.model_copy(update={"openai_model": args.model})

    if args.scripted_action:
        actor = ScriptedActor(args.scripted_action)
    else:
        try:
            actor = OpenAIResponsesActor(settings)
        except ValueError as error:
            parser.error(str(error))

    validators = [NonEmptyValidator()]
    if args.require:
        validators.append(ContainsAllValidator(required=tuple(args.require)))

    budget = BudgetLimits(
        max_iterations=args.max_iterations,
        max_actions=args.max_actions,
        max_recoveries=args.max_recoveries,
    )
    result = LoopEngine(
        observer=ObjectiveObserver(),
        actor=actor,
        verifier=CompositeVerifier(validators),
    ).run(args.objective, budget=budget)

    _print_result(result, as_json=args.json)
    return 0 if result.status is LoopStatus.SUCCEEDED else 2


def _print_result(result: LoopResult, *, as_json: bool) -> None:
    if as_json:
        print(result.model_dump_json(indent=2))
        return

    print(f"status: {result.status}")
    print(f"reason: {result.reason}")
    print(
        "usage: "
        f"{result.usage.iterations} iterations, "
        f"{result.usage.actions} actions, "
        f"{result.usage.recoveries} recoveries"
    )
    print("output:")
    print(result.final_output or "")


if __name__ == "__main__":
    raise SystemExit(main())
