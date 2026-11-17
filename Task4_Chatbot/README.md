# Task 4 - Rule-Based Interactive Terminal Chatbot

A customer-support bot for a fictional shop ("TechNest Electronics") driven by `faq.json`.

## Run

```bash
python chatbot.py          # interactive
python chatbot.py --demo   # scripted conversation (outputs/demo_run.txt)
```

## Features

* Conversation flow: greeting -> intent identification -> resolution -> exit (a small `State` enum).
* Normalisation: lowercase, punctuation stripped, whitespace collapsed.
* Whole-word keyword matching with `re` (so "hi" never matches "shipping").
* Multi-intent answers: "Do you ship fast and what is the refund policy?" returns both answers.
* Regex extraction of order IDs such as `TN-48213`.
* Fallback replies (rotating) when no intent matches, and a prompt on empty input.
* Exit commands: `bye`, `exit`, `quit`, `goodbye`.
* Missing or corrupt `faq.json` falls back to minimal built-in data.

## Extending

Add a new block to `faq.json -> intents` with `keywords` and `response`. Placeholders like `{hours}`, `{phone}` and `{email}` are filled from the `business` section.

## Output

See [`outputs/demo_run.txt`](outputs/demo_run.txt).
