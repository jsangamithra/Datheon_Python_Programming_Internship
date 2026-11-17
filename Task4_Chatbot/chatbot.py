"""Task 4 - Rule-Based Interactive Terminal Assistant / Chatbot.

Pipeline:  greeting -> intent identification (keywords + regex) -> resolution -> exit

* Intents and answers are loaded from faq.json (falls back gracefully if missing/corrupt).
* Input is normalised (lowercase, punctuation stripped, whitespace collapsed).
* Multi-intent: "what are your hours and do you offer refunds?" answers BOTH.
* Order IDs like TN-12345 are extracted with a regular expression.
* Fallback replies when confidence is low; exit with bye / exit / quit.
* Scripted demo for the outputs folder:  python chatbot.py --demo
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from enum import Enum
from itertools import cycle
from pathlib import Path

FAQ_PATH = Path(__file__).with_name("faq.json")
EXIT_WORDS = {"bye", "exit", "quit", "goodbye"}
ORDER_ID_RE = re.compile(r"\b(?:tn|TN)[-\s]?(\d{4,6})\b")

DEFAULT_DATA = {
    "business": {"name": "Support"},
    "intents": {"greeting": {"keywords": ["hello", "hi"], "response": "Hello! How can I help?"}},
    "fallback": ["Sorry, I didn't understand that."],
}


class State(Enum):
    GREETING = "greeting"
    LISTENING = "listening"
    EXIT = "exit"


def load_data(path: Path = FAQ_PATH) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[warning] could not load {path.name}: {exc}. Using minimal built-in data.")
        return DEFAULT_DATA


def normalise(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", " ", text)       # strip punctuation, keep hyphen for order IDs
    return re.sub(r"\s+", " ", text).strip()


def keyword_hit(keyword: str, text: str) -> bool:
    """Whole-word / whole-phrase match so 'hi' does not match 'shipping'."""
    return re.search(rf"\b{re.escape(keyword)}\b", text) is not None


class ChatBot:
    def __init__(self, data: dict):
        self.data = data
        self.biz = data.get("business", {})
        self.intents = data.get("intents", {})
        self._fallbacks = cycle(data.get("fallback", DEFAULT_DATA["fallback"]))
        self.state = State.GREETING

    # ---- intent detection -------------------------------------------------
    def detect_intents(self, text: str) -> list[tuple[str, int]]:
        """Return [(intent, score)] sorted by score; score = number of keyword hits."""
        scored = []
        for name, spec in self.intents.items():
            score = sum(1 for kw in spec["keywords"] if keyword_hit(kw, text))
            if score:
                scored.append((name, score))
        return sorted(scored, key=lambda x: -x[1])

    def respond(self, raw: str) -> str:
        text = normalise(raw)
        if not text:
            return "Please type something - I'm listening."
        if set(text.split()) & EXIT_WORDS:
            self.state = State.EXIT
            return "Thank you for contacting us. Goodbye!"

        # regex: order tracking with ID
        match = ORDER_ID_RE.search(raw)
        if match:
            self.state = State.LISTENING
            return (f"Order TN-{match.group(1)} found: status = 'Shipped', "
                    "expected delivery in 2 business days.")

        found = self.detect_intents(text)
        # greeting alone only counts when nothing else was asked
        if len(found) > 1:
            found = [f for f in found if f[0] != "greeting"] or found
        if not found:
            return next(self._fallbacks)

        self.state = State.LISTENING
        replies = []
        for name, _ in found:
            reply = self.intents[name]["response"]
            replies.append(reply.format(**self.biz) if "{" in reply else reply)
        return "\n".join(f"- {r}" for r in replies) if len(replies) > 1 else replies[0]


def run_interactive(bot: ChatBot) -> None:
    print(f"=== {bot.biz.get('name', 'Support')} Assistant ===  (type 'bye' to exit)")
    while bot.state is not State.EXIT:
        try:
            raw = input("You : ")
        except (EOFError, KeyboardInterrupt):
            print("\nBot : Goodbye!")
            break
        print(f"Bot : {bot.respond(raw)}\n")


def run_demo(bot: ChatBot) -> None:
    script = ["Hello!", "What are your opening hours?", "Do you ship fast and what is the refund policy?",
              "Is there a warranty on laptops? Can I pay by UPI?", "Track my order TN-48213",
              "   ", "tell me about quantum physics", "asdfgh", "Thanks, bye!"]
    print(f"=== {bot.biz.get('name')} Assistant (scripted demo) ===\n")
    for line in script:
        print(f"You : {line!r}")
        print(f"Bot : {bot.respond(line)}\n")
        if bot.state is State.EXIT:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    chatbot = ChatBot(load_data())
    run_demo(chatbot) if args.demo else run_interactive(chatbot)
