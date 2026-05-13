from __future__ import annotations

import math
from collections import Counter, defaultdict
from pathlib import Path

WORD_LENGTH = 5
MISS = "b"
PRESENT = "y"
CORRECT = "g"
WIN_FEEDBACK = CORRECT * WORD_LENGTH


def load_words(path: str | Path | None = None) -> list[str]:
    """Load five-letter words from the project word list."""
    word_path = Path(path) if path else Path(__file__).with_name("wordlist.txt")
    with word_path.open("r", encoding="utf-8") as file:
        words = [
            line.strip().lower()
            for line in file
            if len(line.strip()) == WORD_LENGTH and line.strip().isalpha()
        ]
    return sorted(set(words))


def get_feedback(guess: str, answer: str) -> str:
    """Return Wordle feedback as g/y/b for a guess against an answer."""
    guess = normalize_word(guess)
    answer = normalize_word(answer)
    feedback = [MISS] * WORD_LENGTH
    remaining = Counter()

    for index, letter in enumerate(guess):
        if letter == answer[index]:
            feedback[index] = CORRECT
        else:
            remaining[answer[index]] += 1

    for index, letter in enumerate(guess):
        if feedback[index] == CORRECT:
            continue
        if remaining[letter] > 0:
            feedback[index] = PRESENT
            remaining[letter] -= 1

    return "".join(feedback)


def normalize_word(word: str) -> str:
    normalized = word.strip().lower()
    if len(normalized) != WORD_LENGTH or not normalized.isalpha():
        raise ValueError(f"Expected a {WORD_LENGTH}-letter word, got {word!r}.")
    return normalized


def normalize_feedback(feedback: str) -> str:
    cleaned = feedback.strip().lower()
    aliases = {
        "0": MISS,
        "1": PRESENT,
        "2": CORRECT,
        "m": MISS,
        "x": MISS,
        "-": MISS,
        "b": MISS,
        "n": MISS,
        "y": PRESENT,
        "p": PRESENT,
        "g": CORRECT,
        "c": CORRECT,
    }
    translated = "".join(aliases.get(char, char) for char in cleaned)
    if len(translated) != WORD_LENGTH or any(char not in "byg" for char in translated):
        raise ValueError("Feedback must be five characters using b/y/g or 0/1/2.")
    return translated


def filter_words(possible_answers: list[str], guess: str, feedback: str) -> list[str]:
    guess = normalize_word(guess)
    feedback = normalize_feedback(feedback)
    return [word for word in possible_answers if get_feedback(guess, word) == feedback]


def score_guess(guess: str, possible_answers: list[str]) -> dict[str, float]:
    """Score a guess by how much it partitions the remaining answer set."""
    partitions: dict[str, int] = defaultdict(int)
    for answer in possible_answers:
        partitions[get_feedback(guess, answer)] += 1

    answer_count = len(possible_answers)
    expected_remaining = sum(size * size for size in partitions.values()) / answer_count
    entropy = -sum((size / answer_count) * math.log2(size / answer_count) for size in partitions.values())
    worst_bucket = max(partitions.values())
    return {
        "entropy": entropy,
        "expected_remaining": expected_remaining,
        "worst_bucket": worst_bucket,
        "groups": len(partitions),
    }


def choose_best_guess(
    possible_answers: list[str],
    allowed_guesses: list[str] | None = None,
    limit: int | None = None,
) -> tuple[str, list[tuple[str, dict[str, float]]]]:
    """Choose the highest-information guess and return ranked candidates."""
    if not possible_answers:
        raise ValueError("No possible answers remain.")

    allowed = allowed_guesses or possible_answers
    ranked: list[tuple[str, dict[str, float]]] = []
    possible_set = set(possible_answers)

    for guess in allowed:
        scores = score_guess(guess, possible_answers)
        scores["is_possible_answer"] = 1.0 if guess in possible_set else 0.0
        ranked.append((guess, scores))

    ranked.sort(
        key=lambda item: (
            -item[1]["entropy"],
            item[1]["expected_remaining"],
            item[1]["worst_bucket"],
            -item[1]["is_possible_answer"],
            item[0],
        )
    )
    if limit is not None:
        ranked = ranked[:limit]
    return ranked[0][0], ranked


def format_feedback(feedback: str) -> str:
    labels = {MISS: "miss", PRESENT: "present", CORRECT: "correct"}
    return " ".join(labels[char] for char in normalize_feedback(feedback))
