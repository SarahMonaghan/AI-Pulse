# feature.py
# Scores this week's process-type items, features the top ones, and adds
# a diagram, a before/after example, and a takeaway for the guide.

import json

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

# ---------- Settings (change these anytime) ----------
MODEL = "claude-sonnet-5-5"
INPUT_FILE = "data/analyzed.json"
OUTPUT_FILE = "data/featured.json"
HOW_MANY = 3        # number of featured stories per week
MAX_ARROWS = 20     # upper limit on diagram size

# How much each criterion counts toward the total score
WEIGHTS = {"process": 1, "relevance": 1, "complexity": 1}

READER = """You are helping build AI Pulse, a weekly digest for a reader who
works in policy research (including criminal justice), with a background in
psychology, public policy, and product research. She is not a software engineer.

She wants to understand: what AI can newly do; how experts and organizations
use it; design patterns (prompts vs. workflows vs. agents); and practical use
cases for research, policy, and communications teams.

Write in plain language. Explain any technical idea simply."""

SCORE_INSTRUCTIONS = """Score EVERY item below from 1 (low) to 5 (high) on:

- process: how clearly it shows a step-by-step process (a prompt, workflow,
  or agent in action), rather than news or opinion
- relevance: how directly it applies to her work: research, policy,
  communications, or criminal justice teams
- complexity: how many steps, decisions, tools, or loops the process involves

Give a one-sentence reason for each item."""

STORY_INSTRUCTIONS = """This item is a featured story. Fill in the form.

diagram: a Mermaid flowchart showing how the process works.
- The first line must be exactly: flowchart TD
- 6 to 12 steps. Labels in double quotes, plain language, under 6 words.
- Show decision points as diamonds, e.g.  C{"Enough sources?"}
- Label branches on arrows, e.g.  C -->|"No"| B
- If a step repeats (a loop), draw the arrow back to the earlier step.
- Mark who does each step. End the diagram with these three lines exactly:
    classDef person fill:#F3F4F6,stroke:#6B7280,color:#111827
    classDef ai fill:#EEF2FF,stroke:#6366F1,color:#111827
    classDef tool fill:#ECFDF5,stroke:#10B981,color:#111827
  then assign every step, e.g.:
    class A person
    class B,C ai
    class D tool
- No subgraphs and no other styling. Do not wrap it in ``` marks.

before: 1 to 3 sentences on how this task was typically done before
(by hand, or with a simpler AI setup).

after: 1 to 3 sentences on how it works with the approach in this item.

guide_takeaway: one sentence on what this example teaches about choosing
between a prompt, a workflow, or an agent."""


# ---------- The forms Claude fills in ----------
class Score(BaseModel):
    number: int
    process: int
    relevance: int
    complexity: int
    reason: str


class Scores(BaseModel):
    scores: list[Score]


class Story(BaseModel):
    diagram: str
    before: str
    after: str
    guide_takeaway: str


# ---------- Helper tools ----------
def ask(instructions, content, form):
    """Send text to Claude and get back a filled-in form."""
    response = client.messages.parse(
        model=MODEL,
        max_tokens=8000,
        system=READER,
        messages=[{"role": "user", "content": f"{instructions}\n\n{content}"}],
        output_format=form,
    )
    if response.parsed_output is None:
        raise ValueError(f"no complete answer (stop reason: {response.stop_reason})")
    return response.parsed_output


def total(score):
    """Weighted total, with each score kept between 1 and 5."""
    def clamp(value):
        return max(1, min(5, value))
    return (
        WEIGHTS["process"] * clamp(score.process)
        + WEIGHTS["relevance"] * clamp(score.relevance)
        + WEIGHTS["complexity"] * clamp(score.complexity)
    )


def check_diagram(diagram):
    """Basic check. Returns the diagram, or None if it looks broken."""
    diagram = diagram.replace("```mermaid", "").replace("```", "").strip()
    lines = [line.strip() for line in diagram.splitlines() if line.strip()]
    if not lines or lines[0] not in ("flowchart TD", "flowchart LR"):
        return None
    arrows = sum(line.count("-->") for line in lines)
    if arrows < 1 or arrows > MAX_ARROWS:
        return None
    return diagram


# ---------- Main run ----------
load_dotenv()
client = anthropic.Anthropic()

with open(INPUT_FILE, encoding="utf-8") as f:
    items = json.load(f)

# Only items that describe a prompt, workflow, or agent
candidates = [item for item in items if item["level"].lower() != "not_applicable"]
print(f"{len(candidates)} of {len(items)} items describe a process.\n")

menu = "\n\n".join(
    f"{n}. {item['title']} ({item['source']}) [level: {item['level']}]\n"
    f"{item['plain_summary']}"
    for n, item in enumerate(candidates, start=1)
)

scores = ask(SCORE_INSTRUCTIONS, menu, Scores).scores
scores = [s for s in scores if 1 <= s.number <= len(candidates)]
scores.sort(key=total, reverse=True)

# Print the scoreboard so you can see the reasoning
print("Score  P R C  Title")
for s in scores:
    title = candidates[s.number - 1]["title"][:55]
    print(f" {total(s):>3}   {s.process} {s.relevance} {s.complexity}  {title}")
print()

featured = []
for s in scores[:HOW_MANY]:
    item = candidates[s.number - 1]
    print(f"Featuring: {item['title'][:70]}")

    content = (
        f"Title: {item['title']}\n"
        f"Source: {item['source']}\n"
        f"Summary: {item['summary']}\n"
        f"Plain summary: {item['plain_summary']}"
    )

    try:
        story = ask(STORY_INSTRUCTIONS, content, Story)
    except Exception as error:
        print(f"  ERROR -> {error}")
        continue

    diagram = check_diagram(story.diagram)
    if diagram is None:
        print("  Diagram failed the basic check, so it was left out.")

    featured.append({
        **item,
        "scores": {"process": s.process, "relevance": s.relevance,
                   "complexity": s.complexity, "total": total(s)},
        "pick_reason": s.reason,
        "diagram": diagram,
        "before": story.before,
        "after": story.after,
        "guide_takeaway": story.guide_takeaway,
    })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(featured, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(featured)} featured stories to {OUTPUT_FILE}")