from __future__ import annotations

import argparse

from diagnostics import best_words, simulate
from interactive import run_interactive


def main() -> None:
    parser = argparse.ArgumentParser(description="WordleBot: assistant and diagnostic solver")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("interactive", help="Start the feedback-driven solving assistant")

    best_parser = subparsers.add_parser("best", help="Find the best opening guesses")
    best_parser.add_argument("-n", "--count", type=int, default=10)

    simulate_parser = subparsers.add_parser("simulate", help="Test bot accuracy on random answers")
    simulate_parser.add_argument("-n", "--rounds", type=int, default=100)
    simulate_parser.add_argument("--seed", type=int, default=None)
    simulate_parser.add_argument("--first", default=None, help="Optional fixed first guess")
    simulate_parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    if args.command in (None, "interactive"):
        run_interactive()
    elif args.command == "best":
        best_words(args.count)
    elif args.command == "simulate":
        simulate(args.rounds, args.seed, args.first, args.verbose)


if __name__ == "__main__":
    main()
