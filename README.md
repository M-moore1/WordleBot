# WordleBot

A command-line Wordle solver that uses `wordlist.txt`.

It has two main modes:

1. Interactive assistant: enter your guesses and the feedback from Wordle, and the bot recommends the next highest-information guess.
2. Diagnostics: rank opening words, solve a known answer, or simulate random answers to estimate bot accuracy.

## Run

From this folder:

```bash
python3 WordleBot.py
```

That starts interactive mode. Press Enter at the guess prompt to use the bot's suggested word.

Feedback uses:

- `g` for green/correct
- `y` for yellow/present
- `b` for gray/miss

Example:

```text
Feedback for RAISE: bygbb
```

You can also type `2/1/0` instead of `g/y/b`.

## Diagnostics

Find best opening guesses:

```bash
python3 WordleBot.py best -n 10
```

Simulate 100 random games:

```bash
python3 WordleBot.py simulate -n 100 --seed 7
```

Run the diagnostic module directly:

```bash
python3 diagnostics.py solve CRANE
python3 diagnostics.py simulate -n 500 --first RAISE
```

## How It Works

The solver scores guesses by information gain. For each possible guess, it checks how the guess would split the remaining answer list into feedback groups, then prefers guesses with high entropy, low average remaining answers, and a smaller worst-case bucket.

This is not machine learning; for a word list this size, exact information scoring is faster, more explainable, and reliable.
