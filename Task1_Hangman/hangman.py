"""Task 1 - Hangman Word Guessing Game (Console).

Features
--------
* Loads a word list from words.txt (falls back to a built-in list).
* ASCII gallows art that updates with every wrong guess (6 attempts).
* Tracks guessed letters in sets; duplicate guesses are NOT penalised.
* Clean victory / defeat screens.
* Deterministic demo mode:  python hangman.py --demo   (used to create outputs/)
"""
from __future__ import annotations

import argparse
import random
import string
from pathlib import Path

MAX_MISTAKES = 6
WORDS_FILE = Path(__file__).with_name("words.txt")
FALLBACK_WORDS = ["python", "variable", "function", "iterator", "decorator",
                  "inheritance", "algorithm", "recursion", "exception", "module"]

STAGES = [
    r"""
      +---+
      |   |
          |
          |
          |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
          |
          |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
     /|\  |
          |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
     /|\  |
     /    |
          |
    =========""",
    r"""
      +---+
      |   |
      O   |
     /|\  |
     / \  |
          |
    =========""",
]


def load_words(path: Path = WORDS_FILE) -> list[str]:
    """Read alphabetic words (4+ letters) from file; fall back if missing."""
    try:
        words = [w.strip().lower() for w in path.read_text(encoding="utf-8").splitlines()]
        words = [w for w in words if w.isalpha() and len(w) >= 4]
        return words or FALLBACK_WORDS
    except OSError:
        return FALLBACK_WORDS


def mask_word(secret: str, correct: set[str]) -> str:
    """Return e.g. '_ A _ H E O N' style masked string."""
    return " ".join(ch.upper() if ch in correct else "_" for ch in secret)


def render(secret: str, correct: set[str], wrong: set[str]) -> str:
    lines = [
        STAGES[len(wrong)],
        "",
        f"  Word   : {mask_word(secret, correct)}",
        f"  Wrong  : {' '.join(sorted(wrong)).upper() or '-'}   "
        f"({MAX_MISTAKES - len(wrong)} attempt(s) left)",
    ]
    return "\n".join(lines)


def validate_guess(raw: str, correct: set[str], wrong: set[str]) -> tuple[str | None, str]:
    """Return (letter or None, message). None means 'do not count this turn'."""
    guess = raw.strip().lower()
    if len(guess) != 1 or guess not in string.ascii_lowercase:
        return None, "Please enter exactly ONE letter (a-z)."
    if guess in correct or guess in wrong:
        return None, f"You already guessed '{guess.upper()}'. No penalty - try another."
    return guess, ""


def play(secret: str, input_fn=input, print_fn=print) -> bool:
    """Play one round. Returns True on win. input_fn is injectable for demos/tests."""
    correct: set[str] = set()
    wrong: set[str] = set()
    letters = set(secret)

    print_fn("\n=== HANGMAN ===  Guess the word, one letter at a time.")
    while len(wrong) < MAX_MISTAKES and not letters <= correct:
        print_fn(render(secret, correct, wrong))
        try:
            raw = input_fn("\nYour guess: ")
        except (EOFError, KeyboardInterrupt):
            print_fn("\nGame aborted.")
            return False
        guess, msg = validate_guess(raw, correct, wrong)
        if guess is None:
            print_fn(f"  ! {msg}")
            continue
        if guess in letters:
            correct.add(guess)
            print_fn(f"  + Nice! '{guess.upper()}' is in the word.")
        else:
            wrong.add(guess)
            print_fn(f"  - Sorry, '{guess.upper()}' is not in the word.")

    if letters <= correct:
        print_fn(render(secret, correct, wrong))
        print_fn("\n*********************************")
        print_fn(f"   VICTORY!  The word was '{secret.upper()}'")
        print_fn(f"   Mistakes made: {len(wrong)}/{MAX_MISTAKES}")
        print_fn("*********************************")
        return True
    print_fn(STAGES[MAX_MISTAKES])
    print_fn("\n#################################")
    print_fn(f"   GAME OVER.  The word was '{secret.upper()}'")
    print_fn("#################################")
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Console Hangman")
    parser.add_argument("--demo", action="store_true",
                        help="run scripted win + loss games (non-interactive)")
    args = parser.parse_args()

    if args.demo:
        # includes a duplicate ('p'), a wrong letter ('x') and an invalid input ('!')
        script_win = iter(["p", "p", "x", "y", "t", "h", "!", "o", "n"])
        def fake(prompt, it=script_win):
            val = next(it)
            print(f"{prompt}{val}")
            return val
        print(">>> DEMO 1: winning game (secret = python), includes duplicate + invalid input")
        play("python", input_fn=fake)

        script_lose = iter(list("zqxwvu"))
        def fake2(prompt, it=script_lose):
            val = next(it)
            print(f"{prompt}{val}")
            return val
        print("\n\n>>> DEMO 2: losing game (secret = decorator)")
        play("decorator", input_fn=fake2)
        return

    words = load_words()
    while True:
        play(random.choice(words))
        if input("\nPlay again? (y/n): ").strip().lower() != "y":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
