# Task 1 - Hangman Word Guessing Game (Console)

Terminal Hangman with ASCII gallows art, 6 allowed mistakes, and duplicate-guess protection.

## Run

```bash
python hangman.py          # interactive, random word from words.txt
python hangman.py --demo   # scripted win + loss (how outputs/demo_run.txt was produced)
```

## Features

* Word list loaded from `words.txt` (built-in fallback list if the file is missing).
* Correct guesses stored in a `set`, wrong guesses in another `set`, so repeating a letter never costs an attempt.
* Masked word display, e.g. `P _ T H _ N`.
* 7 ASCII gallows stages that advance with each wrong guess.
* Input validation: only a single letter a-z is accepted.
* Victory and game-over screens, plus a play-again prompt.
* `play()` takes injectable `input_fn` / `print_fn`, which makes it testable and demo-able.

## Output

See [`outputs/demo_run.txt`](outputs/demo_run.txt) - it shows a win (including a duplicate and an invalid input) and a loss.
