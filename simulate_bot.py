import random
from collections import Counter
from tqdm import tqdm

# Load word list
with open('Wordle/wordlist.txt', 'r') as f:
    ALL_WORDS = [line.strip().upper() for line in f if len(line.strip()) == 5]

def get_feedback(guess, answer):
    feedback = ['gray'] * 5
    answer_chars = list(answer)
    guess_chars = list(guess)

    # Green pass
    for i in range(5):
        if guess_chars[i] == answer_chars[i]:
            feedback[i] = 'green'
            answer_chars[i] = None
            guess_chars[i] = None

    # Yellow pass
    for i in range(5):
        if guess_chars[i] and guess_chars[i] in answer_chars:
            feedback[i] = 'yellow'
            answer_chars[answer_chars.index(guess_chars[i])] = None

    return feedback

def apply_feedback(words, guess, feedback):
    result = []
    for word in words:
        match = True
        used = [False] * 5

        for i in range(5):
            if feedback[i] == 'green':
                if word[i] != guess[i]:
                    match = False
                    break
                used[i] = True
        if not match:
            continue

        for i in range(5):
            if feedback[i] == 'yellow':
                if guess[i] not in word or word[i] == guess[i]:
                    match = False
                    break
            elif feedback[i] == 'gray':
                allowed = sum(1 for j in range(5) if guess[j] == guess[i] and feedback[j] in ['green', 'yellow'])
                if word.count(guess[i]) > allowed:
                    match = False
                    break
        if match:
            result.append(word)
    return result

def simulate_game(answer, starting_word="CRANE"):
    guess = starting_word
    possible_words = list(ALL_WORDS)

    for attempt in range(1, 7):
        feedback = get_feedback(guess, answer)
        if guess == answer:
            return attempt
        possible_words = apply_feedback(possible_words, list(guess), feedback)
        if not possible_words:
            return 7  # fail
        guess = possible_words[0]
    return 7  # failed to guess in 6

def run_simulation(rounds=1000, starting_word="CRANE"):
    total_attempts = 0
    solved = 0
    results = []

    for _ in tqdm(range(rounds), desc=f"Simulating with start: {starting_word}"):
        answer = random.choice(ALL_WORDS)
        attempts = simulate_game(answer, starting_word)
        results.append(attempts)
        if attempts <= 6:
            solved += 1
        total_attempts += attempts

    average = total_attempts / rounds
    #print(f"ANSWER:  {answer}")
    print(f"Start word: {starting_word}")
    print(f"Average guesses: {average:.3f}")
    print(f"Solved within 6 guesses: {solved}/{rounds} ({(solved/rounds)*100:.2f}%)")
    print()

    return average, solved

# Try multiple starting words
if __name__ == "__main__":
    candidates = ["CRANE", "SLATE", "AUDIO", "RAISE", "ADIEU", "TRIED"]
    #candidates = ALL_WORDS
    #candidates = random.sample(ALL_WORDS, 100)
    results = []

    for word in candidates:
        avg, solved = run_simulation(1000, starting_word=word)
        results.append((word, avg))

    print("\n=== Best Starters ===")
    results.sort(key=lambda x: x[1])
    for word, avg in results:
        print(f"{word}: {avg:.3f} guesses on average")