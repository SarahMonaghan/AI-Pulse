# collect.py
# Visits each source, keeps the past week's items, and saves them to a file.

import json
import os
from calendar import timegm
from datetime import datetime, timedelta, timezone

import feedparser
from sources import SOURCES

AGENT = "AI-Pulse/0.1 (personal research digest)"
DAYS_BACK = 7
OUTPUT_FILE = "data/items.json"

# arXiv posts hundreds of papers a day, so keep only ones that mention these.
ARXIV_KEYWORDS = [
       "agent", "agentic", "tool use", "tool-use", "multi-agent",
       "workflow", "policy", "government", "public sector",
       "social science", "qualitative", "survey", "criminal justice",
   ]

cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)


def get_date(entry):
    """Return the item's date, or None if the feed doesn't give one."""
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed is None:
        return None
    return datetime.fromtimestamp(timegm(parsed), tz=timezone.utc)


def matches_keywords(entry):
    """Check whether an item's title or summary mentions a keyword."""
    text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
    return any(word in text for word in ARXIV_KEYWORDS)


items = []

for source in SOURCES:
    feed = feedparser.parse(source["url"], agent=AGENT)
    kept = 0

    for entry in feed.entries:
        date = get_date(entry)
        if date is None or date < cutoff:
            continue  # skip: too old or undated
        if "arxiv" in source["url"] and not matches_keywords(entry):
            continue  # skip: off-topic paper

        items.append({
            "source": source["name"],
            "section": source["section"],
            "title": entry.get("title", "(no title)"),
            "link": entry.get("link", ""),
            "date": date.isoformat(),
            "summary": entry.get("summary", "")[:1000],
        })
        kept += 1

    print(f"{source['name']}: kept {kept} of {len(feed.entries)}")

os.makedirs("data", exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(items, f, indent=2, ensure_ascii=False)

print(f"\nSaved {len(items)} items to {OUTPUT_FILE}")