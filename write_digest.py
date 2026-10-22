# write_digest.py
# Turns Claude's cards into one readable weekly digest (Markdown)
# and saves it to the inbox/ folder for review in Obsidian.

import json
import os
from datetime import date

# ---------- Settings ----------
INPUT_FILE = "data/analyzed.json"
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

# ---------- Build the digest ----------
with open(INPUT_FILE, encoding="utf-8") as f:
    items = json.load(f)

today = date.today().isoformat()

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

for section in SECTIONS:
    section_items = [item for item in items if item["section"] == section]
    if not section_items:
        continue

    lines += [f"## {section}", ""]

    for item in section_items:
        level = LEVEL_LABELS.get(item["level"].lower(), item["level"])
        field = FIELD_LABELS.get(item["field"].lower(), item["field"])
        lines += [
            f"### [{item['title']}]({item['link']})",
            f"*{item['source']} · Level: {level} · Field: {field}*",
            "",
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
    '*Add new examples for the "Which tool for which task?" guide here.*',
    "",
]

# ---------- Save ----------
os.makedirs(INBOX, exist_ok=True)
path = os.path.join(INBOX, f"{today}-digest.md")
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Digest draft saved to {path}")