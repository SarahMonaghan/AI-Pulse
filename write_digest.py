# write_digest.py
# Turns Claude's cards into one readable weekly digest (Markdown)
# and saves it to the inbox/ folder for review in Obsidian.

import json
import os
from datetime import date

# ---------- Settings ----------
INPUT_FILE = "data/analyzed.json"
FEATURED_FILE = "data/featured.json"
INBOX = "inbox"

SECTIONS = [
    "New capabilities",
    "What experts are building",
    "Research and policy teams",
    "Research worth knowing",
]

LEVEL_LABELS = {
    "prompt": "Prompt", "workflow": "Workflow",
    "agent": "Agent", "not_applicable": "—",
}
FIELD_LABELS = {
    "policy": "Policy", "communications": "Communications",
    "research": "Research", "criminal_justice": "Criminal Justice",
    "general": "General",
}

DIAGRAM_KEY = "*Diagram key: grey = person · purple = AI · green = tool or data*"


# ---------- Helper tools ----------
def labels(item):
    """Return readable level and field labels for an item."""
    level = LEVEL_LABELS.get(item["level"].lower(), item["level"])
    field = FIELD_LABELS.get(item["field"].lower(), item["field"])
    return level, field


def heading_and_meta(item):
    """The title link and the small grey line under it."""
    level, field = labels(item)
    return [
        f"### [{item['title']}]({item['link']})",
        f"*{item['source']} · Level: {level} · Field: {field}*",
        "",
    ]


# ---------- Load this week's data ----------
with open(INPUT_FILE, encoding="utf-8") as f:
    items = json.load(f)

featured = []
if os.path.exists(FEATURED_FILE):
    with open(FEATURED_FILE, encoding="utf-8") as f:
        featured = json.load(f)
featured_links = {story["link"] for story in featured}

today = date.today().isoformat()

# ---------- Build the digest ----------
lines = [
    "---",
    f"title: AI Pulse — Week of {today}",
    f"date: {today}",
    "type: digest",
    "status: draft",
    "---",
    "",
    f"# AI Pulse — Week of {today}",
    "",
    f"*{len(items)} items this week.*",
    "",
]

# Featured stories first
if featured:
    lines += ["## Featured this week", "", DIAGRAM_KEY, ""]
    for story in featured:
        lines += heading_and_meta(story)
        lines += [story["plain_summary"], ""]
        if story["diagram"]:
            lines += ["```mermaid", story["diagram"], "```", ""]
        lines += [
            f"**Before:** {story['before']}",
            "",
            f"**After:** {story['after']}",
            "",
            f"**Why it matters:** {story['why_it_matters']}",
            "",
        ]

# Regular sections (skipping anything already featured)
for section in SECTIONS:
    section_items = [
        item for item in items
        if item["section"] == section and item["link"] not in featured_links
    ]
    if not section_items:
        continue

    lines += [f"## {section}", ""]
    for item in section_items:
        lines += heading_and_meta(item)
        lines += [
            item["plain_summary"],
            "",
            f"**Why it matters:** {item['why_it_matters']}",
            "",
            f"**Analogy:** {item['analogy']}",
            "",
        ]

# Sections you fill in yourself
lines += [
    "## In Practice",
    "",
    "*Add your own experiments or interviews here.*",
    "",
    "## Guide updates",
    "",
]

if featured:
    for story in featured:
        level, _ = labels(story)
        lines.append(
            f"- **{level}:** {story['guide_takeaway']} "
            f"([{story['title']}]({story['link']}))"
        )
    lines.append("")
else:
    lines += ['*Add new examples for the "Which tool for which task?" guide here.*', ""]

# ---------- Save ----------
os.makedirs(INBOX, exist_ok=True)
path = os.path.join(INBOX, f"{today}-digest.md")
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Digest draft saved to {path}")