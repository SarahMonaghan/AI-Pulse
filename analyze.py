# analyze.py
# Sends each collected item to Claude in two passes:
#   1. a quick keep/skip check (cheap model)
#   2. a full "form" for the items worth keeping (stronger model)

import json
from typing import Literal

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

# ---------- Settings (change these anytime) ----------
TRIAGE_MODEL = "claude-haiku-5-5"   # cheap model for keep/skip
CARD_MODEL = "claude-sonnet-5-5"    # stronger model for writing
INPUT_FILE = "data/items.json"
OUTPUT_FILE = "data/analyzed.json"
SKIPPED_FILE = "data/skipped.json"

# Background briefing Claude reads before every item.
READER = """You are helping build AI Pulse, a weekly digest for a reader who
works in policy research (including criminal justice), with a background in
psychology, public policy, and product research. She is not a software engineer.

She wants to understand: what AI can newly do; how experts and organizations
use it; design patterns (prompts vs. workflows vs. agents); and practical use
cases for research, policy, and communications teams.

Write in plain language. Explain any technical idea simply."""

# Deliberately generous for now. Add to the SKIP list as you review results.
TRIAGE_INSTRUCTIONS = """Decide whether this item could belong in her weekly digest.
Be generous: when in doubt, KEEP.

KEEP anything related to AI: capabilities, products, research, how people or
organizations use it, its effects on work, society, or policy, and big-picture
analysis of where AI is heading.

SKIP only items that are clearly not useful:
- personnel announcements (hires, board appointments)
- funding or investment news
- partner or sales announcements
- topics unrelated to AI

Give your reason in one short sentence."""

CARD_INSTRUCTIONS = """Fill in the form for this item.

Definitions for "level":
- prompt: a single question and answer with AI
- workflow: a fixed series of AI steps that a person designs in advance
- agent: the AI decides its own steps and uses tools to reach a goal
- not_applicable: the item isn't about how a task is set up

Definitions for "field" (pick the best single fit):
- policy, communications, research, criminal_justice, or general

Keep the summary to 2 sentences and "why it matters" to 1 sentence.
List only technical terms that actually appear in the item."""


# ---------- The forms Claude fills in ----------
class Triage(BaseModel):
    keep: bool
    reason: str


class ItemCard(BaseModel):
    plain_summary: str
    why_it_matters: str
    level: Literal["prompt", "workflow", "agent", "not_applicable"]
    field: Literal["policy", "communications", "research", "criminal_justice", "general"]
    analogy: str
    technical_terms: list[str]


# ---------- Helper tools ----------
def describe(item):
    """Turn one collected item into text Claude can read."""
    return (
        f"Source: {item['source']}\n"
        f"Title: {item['title']}\n"
        f"Summary: {item['summary']}"
    )


def ask(model, instructions, item, form, max_tokens):
    """Send one item to Claude and get back a filled-in form."""
    response = client.messages.parse(
        model=model,
        max_tokens=max_tokens,
        system=READER,
        messages=[{"role": "user", "content": f"{instructions}\n\n{describe(item)}"}],
        output_format=form,
    )
    if response.parsed_output is None:
        raise ValueError(f"no complete answer (stop reason: {response.stop_reason})")
    return response.parsed_output


def save(data, path):
    """Write data to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------- Main run ----------
load_dotenv()
client = anthropic.Anthropic()

with open(INPUT_FILE, encoding="utf-8") as f:
    items = json.load(f)

print(f"Analyzing {len(items)} items...\n")
results = []
skipped = []

for item in items:
    title = item["title"][:70]

    try:
        decision = ask(TRIAGE_MODEL, TRIAGE_INSTRUCTIONS, item, Triage, 2000)
        if not decision.keep:
            print(f"skip  {title}")
            skipped.append({
                "source": item["source"],
                "title": item["title"],
                "link": item["link"],
                "reason": decision.reason,
            })
            continue

        card = ask(CARD_MODEL, CARD_INSTRUCTIONS, item, ItemCard, 4000)
    except Exception as error:
        print(f"ERROR {title}  ->  {error}")
        continue

    print(f"KEEP  {title}  [{card.level}, {card.field}]")
    results.append({**item, "keep_reason": decision.reason, **card.model_dump()})

save(results, OUTPUT_FILE)
save(skipped, SKIPPED_FILE)

print(f"\nKept {len(results)}, skipped {len(skipped)}, of {len(items)} total.")
print(f"Saved to {OUTPUT_FILE} and {SKIPPED_FILE}")