from __future__ import annotations

import argparse
import random
from collections import Counter

from solver import WIN_FEEDBACK, choose_best_guess, filter_words, get_feedback, load_words, normalize_word


def solve_answer(answer: str, words: list[str], first_guess: str | None = None, verbose: bool = False) -> int:
    answer = normalize_word(answer)
    possible_answers = words[:]
    guess = first_guess or choose_best_guess(possible_answers, words, limit=1)[0]

    for turn in range(1, 7):
        feedback = get_feedback(guess, answer)
        if verbose:
            print(f"{turn}. {guess.upper()} -> {feedback} ({len(possible_answers)} possible before filter)")
        if feedback == WIN_FEEDBACK:
            return turn

        possible_answers = filter_words(possible_answers, guess, feedback)
        if not possible_answers:
            return 7

        guess_pool = possible_answers if len(possible_answers) > 1 else possible_answers
        guess = choose_best_guess(possible_answers, guess_pool, limit=1)[0]

    return 7


def simulate(rounds: int, seed: int | None, first_guess: str | None, verbose: bool = False) -> None:
    words = load_words()
    rng = random.Random(seed)
    if first_guess is None:
        first_guess = choose_best_guess(words, words, limit=1)[0]
    else:
        first_guess = normalize_word(first_guess)

    results: list[int] = []
    for index in range(rounds):
        answer = rng.choice(words)
        attempts = solve_answer(answer, words, first_guess=first_guess, verbose=verbose and rounds == 1)
        results.append(attempts)
        if verbose and rounds > 1:
            status = "fail" if attempts > 6 else str(attempts)
            print(f"{index + 1:>4}. {answer.upper()} -> {status}")

    solved = sum(1 for attempts in results if attempts <= 6)
    distribution = Counter(results)
    average = sum(results) / len(results)

    print(f"Rounds: {rounds}")
    print(f"First guess: {first_guess.upper()}")
    print(f"Solved: {solved}/{rounds} ({solved / rounds:.1%})")
    print(f"Average turns: {average:.3f}")
    print("Distribution:")
    for turn in range(1, 7):
        print(f"  {turn}: {distribution[turn]}")
    print(f"  fail: {distribution[7]}")


def best_words(count: int) -> None:
    words = load_words()
    _, ranked = choose_best_guess(words, words, limit=count)
    print(f"Best opening guesses from {len(words)} words:")
    for index, (word, scores) in enumerate(ranked, start=1):
        print(
            f"{index:>2}. {word.upper()}  "
            f"entropy={scores['entropy']:.3f}  "
            f"avg_remaining={scores['expected_remaining']:.1f}  "
            f"worst_case={int(scores['worst_bucket'])}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="WordleBot diagnostic tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    simulate_parser = subparsers.add_parser("simulate", help="Run random-answer bot simulations")
    simulate_parser.add_argument("-n", "--rounds", type=int, default=100)
    simulate_parser.add_argument("--seed", type=int, default=None)
    simulate_parser.add_argument("--first", default=None, help="Optional fixed first guess")
    simulate_parser.add_argument("--verbose", action="store_true")

    best_parser = subparsers.add_parser("best", help="Rank best opening guesses")
    best_parser.add_argument("-n", "--count", type=int, default=10)

    solve_parser = subparsers.add_parser("solve", help="Run the bot against a known answer")
    solve_parser.add_argument("answer")
    solve_parser.add_argument("--first", default=None)

    args = parser.parse_args()
    if args.command == "simulate":
        simulate(args.rounds, args.seed, args.first, args.verbose)
    elif args.command == "best":
        best_words(args.count)
    elif args.command == "solve":
        words = load_words()
        first = normalize_word(args.first) if args.first else None
        attempts = solve_answer(args.answer, words, first_guess=first, verbose=True)
        print("Result:", "failed" if attempts > 6 else f"solved in {attempts}")


if __name__ == "__main__":
    main()
