# sources.py
# The places AI Pulse checks each week.
# Each source has a name, a feed URL, and the digest section it usually feeds.

SOURCES = [
    # --- Anthropic ---
    {
        "name": "Anthropic Engineering",
        "url": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
        "section": "What experts are building",
    },
    {
        "name": "Anthropic News",
        "url": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
        "section": "New capabilities",
    },
    {
        "name": "Anthropic Research",
        "url": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
        "section": "Research worth knowing",
    },
    {
        "name": "Claude Blog",
        "url": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_claude.xml",
        "section": "New capabilities",
    },
    # --- Other AI labs ---
    {
        "name": "OpenAI Engineering",
        "url": "https://openai.com/news/engineering/rss.xml",
        "section": "What experts are building",
    },
    {
        "name": "Google DeepMind",
        "url": "https://deepmind.google/blog/rss.xml",
        "section": "New capabilities",
    },
    # --- Practitioners and explainers ---
    {
        "name": "Hamel Husain",
        "url": "https://hamel.dev/index.xml",
        "section": "What experts are building",
    },
    {
        "name": "One Useful Thing",
        "url": "https://www.oneusefulthing.org/feed",
        "section": "Research and policy teams",
    },
    {
        "name": "The Batch",
        "url": "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_the_batch.xml",
        "section": "Research worth knowing",
    },
    # --- Research and policy ---
    {
        "name": "Import AI",
        "url": "https://importai.substack.com/feed",
        "section": "Research worth knowing",
    },
    {
        "name": "arXiv: Computers and Society (cs.CY)",
        "url": "https://rss.arxiv.org/rss/cs.CY",
        "section": "Research and policy teams",
    },
]