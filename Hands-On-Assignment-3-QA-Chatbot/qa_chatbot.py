#!/usr/bin/env python3
"""A terminal Q&A chatbot built on ChatterBot.

Hands-On Assignment 3 — MSCS-633-M20, Advance Artificial Intelligence
University of the Cumberlands

ChatterBot is a machine-learning conversational engine: rather than matching
hand-written rules, it stores every statement it has been trained on together
with the responses that followed, then answers a new input by finding the
closest known statement and returning one of its recorded replies. This program
wraps that engine in a terminal client.

Usage:
    python qa_chatbot.py                 # train on first run, then chat
    python qa_chatbot.py --no-train      # skip training, reuse existing database
    python qa_chatbot.py --retrain       # wipe the database and train from scratch
    python qa_chatbot.py --name Ada      # give the bot a different display name
"""

import argparse
import logging
import os
import sys

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

# ── Configuration ─────────────────────────────────────────────────────────────

# Store the learned conversation database beside this script so the program
# behaves the same no matter which directory it is launched from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "chatbot_database.sqlite3")

# Corpora to train on. Each is a module path inside the chatterbot_corpus
# package; "greetings" and "conversations" carry ordinary small talk, while
# the others give the bot something to say on common question topics.
TRAINING_CORPORA = [
    "chatterbot.corpus.english.greetings",
    "chatterbot.corpus.english.conversations",
    "chatterbot.corpus.english.computers",
    "chatterbot.corpus.english.science",
    "chatterbot.corpus.english.humor",
]

# Below this similarity score the bot admits it does not know rather than
# returning the nearest match. Without a threshold ChatterBot will always answer
# with *something*, which reads as confident nonsense on unfamiliar input.
CONFIDENCE_THRESHOLD = 0.65

DEFAULT_RESPONSE = "I'm not sure how to answer that yet. Try asking me something else."

# Words that end the session. Checked case-insensitively.
EXIT_COMMANDS = {"quit", "exit", "bye", "goodbye"}


# ── Bot construction ──────────────────────────────────────────────────────────

def build_chatbot(name: str) -> ChatBot:
    """Create the ChatBot instance and its storage/logic configuration.

    The SQL storage adapter persists what the bot knows to a SQLite file, so
    training survives between runs. BestMatch compares the user's input against
    stored statements and picks the closest; the threshold and default response
    configured here are what keep it from bluffing.
    """
    return ChatBot(
        name,
        storage_adapter="chatterbot.storage.SQLStorageAdapter",
        database_uri=f"sqlite:///{DATABASE_PATH}",
        logic_adapters=[
            {
                "import_path": "chatterbot.logic.BestMatch",
                "default_response": DEFAULT_RESPONSE,
                "maximum_similarity_threshold": CONFIDENCE_THRESHOLD,
            }
        ],
    )


def train(bot: ChatBot) -> None:
    """Train the bot on the bundled English corpora.

    Training is the expensive step — it parses every statement in each corpus
    and writes it to the database — so the caller decides when to run it rather
    than paying the cost on every launch.
    """
    trainer = ChatterBotCorpusTrainer(bot)
    print("Training on the English corpora. This takes a minute on first run...\n")
    trainer.train(*TRAINING_CORPORA)
    print("\nTraining complete.\n")


def database_exists() -> bool:
    """Report whether a previously trained database is already on disk."""
    return os.path.exists(DATABASE_PATH) and os.path.getsize(DATABASE_PATH) > 0


# ── Terminal client ───────────────────────────────────────────────────────────

def chat_loop(bot: ChatBot) -> None:
    """Read user input and print bot responses until the user exits.

    Ctrl-C and Ctrl-D are caught so that interrupting the program produces a
    clean goodbye instead of a traceback.
    """
    print(f"Chatting with {bot.name}. Type 'quit' to leave.\n")

    while True:
        try:
            user_input = input("user: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nbot: Goodbye.")
            return

        # Ignore empty lines rather than asking the engine to match "".
        if not user_input:
            continue

        if user_input.lower() in EXIT_COMMANDS:
            print("bot: Goodbye.")
            return

        response = bot.get_response(user_input)
        print(f"bot: {response}")


# ── Entry point ───────────────────────────────────────────────────────────────

def parse_arguments() -> argparse.Namespace:
    """Define and read the command-line interface."""
    parser = argparse.ArgumentParser(
        description="A terminal Q&A chatbot built with ChatterBot."
    )
    parser.add_argument(
        "--name",
        default="QA Bot",
        help="display name for the bot (default: %(default)s)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--no-train",
        action="store_true",
        help="skip training and reuse the existing database",
    )
    group.add_argument(
        "--retrain",
        action="store_true",
        help="delete the existing database and train from scratch",
    )
    return parser.parse_args()


def main() -> int:
    """Wire up the bot according to the command-line flags and start chatting."""
    args = parse_arguments()

    # ChatterBot logs training progress at INFO; quiet it so the transcript
    # the user sees is just the conversation.
    logging.basicConfig(level=logging.WARNING)

    if args.retrain and os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        print("Existing database removed.")

    # Train when the user asked for it, or when there is simply nothing to
    # talk from yet. --no-train on an empty database is a user error worth
    # reporting rather than silently producing a bot that answers nothing.
    needs_training = args.retrain or not database_exists()

    if needs_training and args.no_train:
        print(
            "No trained database found, so --no-train leaves the bot with "
            "nothing to say. Run without --no-train first.",
            file=sys.stderr,
        )
        return 1

    bot = build_chatbot(args.name)

    if needs_training:
        train(bot)

    chat_loop(bot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
