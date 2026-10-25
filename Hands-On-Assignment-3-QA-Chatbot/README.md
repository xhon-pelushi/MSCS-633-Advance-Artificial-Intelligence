# Hands-On Assignment 3 — Q&A Chatbot with Python

A terminal client that holds a conversation with a [ChatterBot](https://chatterbot.readthedocs.io/)-backed
bot, built for MSCS-633-M20 (Advance Artificial Intelligence), University of the Cumberlands.

ChatterBot is a retrieval-based conversational engine: it stores the statements it was
trained on along with the responses that followed them, then answers new input by finding
the closest known statement. No reply text is hard-coded in this program.

## Requirements

- Python 3.12
- Dependencies pinned in [`requirements.txt`](requirements.txt)

ChatterBot 1.0.x does not install on Python 3.12 — it pins obsolete dependency versions and
fails during resolution. This project pins the maintained 1.2.x line.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

The spaCy model is fetched separately because it ships as a release asset rather than on PyPI.

> `PyYAML` is an optional dependency of ChatterBot that is **not** installed automatically,
> but the training corpora are YAML files. Without it, training fails with
> `OptionalDependencyImportError`. It is pinned in the manifest for that reason.

## Usage

```bash
python qa_chatbot.py
```

| Flag | Effect |
|------|--------|
| *(none)* | Trains on first run, then chats; reuses the database afterwards |
| `--no-train` | Skip training and reuse the existing database |
| `--retrain` | Delete the database and train from scratch |
| `--name NAME` | Change the bot's display name (default: `QA Bot`) |

Type `quit`, `exit`, `bye`, or `goodbye` to end the session. `Ctrl-C` and `Ctrl-D` also exit
cleanly.

## Example session

```
user: Good morning! How are you doing?
bot: I am doing well, how about you?
user: What is a computer?
bot: A computer is an electronic device which takes information in digital form and
     performs a series of operations based on predetermined instructions to give some output.
user: Tell me a joke
bot: Did you hear the one about the mountain goats in the Andes? It was "ba a a a a a d".
user: quit
bot: Goodbye.
```

## Design notes

**Storage.** A SQLite database written beside the script persists what the bot has learned,
so training is paid for once. The path resolves relative to the script rather than the
working directory, so the program behaves identically wherever it is launched from.

**Confidence threshold.** `BestMatch` is configured with a maximum similarity threshold of
`0.65` and a default response. Left unconfigured it always returns its nearest neighbour
however distant, which produces fluent but unrelated answers. The threshold is what lets the
bot say it does not know:

```
user: What is the airspeed velocity of an unladen swallow?
bot: I'm not sure how to answer that yet. Try asking me something else.
```

**Training corpora.** Five English corpora — greetings, conversations, computers, science,
and humor — chosen to cover both small talk and factual questions.

## Files

| File | Purpose |
|------|---------|
| `qa_chatbot.py` | The chatbot and terminal client |
| `requirements.txt` | Pinned dependency manifest |
| `screenshot_*.png` | Terminal captures of setup and real runs |
| `Hands-On Assignment 3 - Q&A Chatbot with Python.docx` | Written report |
