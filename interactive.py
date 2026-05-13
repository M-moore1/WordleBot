from __future__ import annotations

from solver import WIN_FEEDBACK, choose_best_guess, filter_words, load_words, normalize_feedback, normalize_word


def run_interactive() -> None:
    words = load_words()
    possible_answers = words[:]
    history: list[tuple[str, str]] = []

    print("WordleBot interactive assistant")
    print("Feedback format: g = green, y = yellow, b = gray/black. Example: bygbb")
    print("You can also use 2/1/0 for green/yellow/gray.\n")

    for turn in range(1, 7):
        suggestion, ranked = choose_best_guess(possible_answers, words, limit=5)
        print(f"Turn {turn}: {len(possible_answers)} possible answer(s)")
        print("Best guesses:")
        for word, scores in ranked:
            marker = "*" if word in possible_answers else " "
            print(
                f"  {marker} {word.upper()}  "
                f"entropy={scores['entropy']:.2f}  "
                f"avg_remaining={scores['expected_remaining']:.1f}"
            )

        guess = prompt_guess(suggestion, words)
        feedback = prompt_feedback(guess)
        history.append((guess, feedback))

        if feedback == WIN_FEEDBACK:
            print(f"Solved. Nice: {guess.upper()} on turn {turn}.")
            return

        possible_answers = filter_words(possible_answers, guess, feedback)
        if not possible_answers:
            print("No possible answers remain. One of the feedback rows may be inconsistent.")
            print_history(history)
            return
        print()

    print("Six turns used.")
    print(f"Remaining answers: {', '.join(word.upper() for word in possible_answers[:25])}")
    if len(possible_answers) > 25:
        print(f"...and {len(possible_answers) - 25} more.")


def prompt_guess(suggestion: str, words: list[str]) -> str:
    word_set = set(words)
    while True:
        raw = input(f"Guess [{suggestion.upper()}]: ").strip()
        guess = suggestion if raw == "" else raw
        try:
            guess = normalize_word(guess)
        except ValueError as error:
            print(error)
            continue
        if guess not in word_set:
            print("That word is not in wordlist.txt.")
            continue
        return guess


def prompt_feedback(guess: str) -> str:
    while True:
        raw = input(f"Feedback for {guess.upper()}: ")
        try:
            return normalize_feedback(raw)
        except ValueError as error:
            print(error)


def print_history(history: list[tuple[str, str]]) -> None:
    if not history:
        return
    print("History:")
    for guess, feedback in history:
        print(f"  {guess.upper()} {feedback}")


if __name__ == "__main__":
    run_interactive()
