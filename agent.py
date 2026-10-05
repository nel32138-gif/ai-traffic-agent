import os
import json
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests


# =========================
# CONFIG
# =========================

AGENT_NAME = "AI Traffic Agent"
STATE_FILE = "state.json"

# RSS sources.
# На первом этапе используем RSS, потому что это проще и стабильнее,
# чем пытаться парсить произвольные сайты.
RSS_SOURCES = [
    "https://news.ycombinator.com/rss",
    "https://www.reddit.com/r/Entrepreneur/.rss",
    "https://www.reddit.com/r/SideProject/.rss",
]

KEYWORDS = [
    "traffic",
    "automation",
    "ai",
    "artificial intelligence",
    "saas",
    "marketing",
    "startup",
    "business",
    "tool",
    "bot",
]


# =========================
# STATE
# =========================

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"processed": []}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"processed": []}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# =========================
# HELPERS
# =========================

def make_id(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def keyword_score(text):
    text = text.lower()

    score = 0
    matched = []

    for keyword in KEYWORDS:
        if keyword in text:
            score += 1
            matched.append(keyword)

    return score, matched


def get_domain(url):
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


# =========================
# RSS
# =========================

def fetch_rss(url):
    headers = {
        "User-Agent": "AI-Traffic-Agent/0.1"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    return response.text


def parse_rss(xml):
    """
    Very small RSS parser using only Python's standard library.
    """

    import xml.etree.ElementTree as ET

    root = ET.fromstring(xml)

    results = []

    for item in root.findall(".//item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        description = item.findtext("description") or ""
        pub_date = item.findtext("pubDate") or ""

        results.append({
            "title": title.strip(),
            "url": link.strip(),
            "description": description.strip(),
            "published": pub_date.strip(),
        })

    return results


# =========================
# ANALYSIS
# =========================

def analyze_item(item):
    text = (
        item["title"]
        + " "
        + item["description"]
    )

    score, matched = keyword_score(text)

    return {
        "title": item["title"],
        "url": item["url"],
        "domain": get_domain(item["url"]),
        "score": score,
        "matched_keywords": matched,
        "published": item["published"],
    }


# =========================
# MAIN AGENT
# =========================

def run_agent():

    print("=" * 60)
    print(AGENT_NAME)
    print("Started:", datetime.now(timezone.utc).isoformat())
    print("=" * 60)

    state = load_state()

    processed = set(state.get("processed", []))

    discovered = []
    new_ids = []

    for source in RSS_SOURCES:

        print("\nSOURCE:", source)

        try:
            xml = fetch_rss(source)
            items = parse_rss(xml)

        except Exception as error:
            print("Source error:", error)
            continue

        for item in items:

            if not item["url"]:
                continue

            item_id = make_id(item["url"])

            if item_id in processed:
                continue

            analyzed = analyze_item(item)

            discovered.append(analyzed)
            new_ids.append(item_id)

    # Sort by relevance
    discovered.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    print("\nNEW ITEMS:", len(discovered))

    print("\nTOP RESULTS")
    print("-" * 60)

    for item in discovered[:10]:

        print("\nTITLE:", item["title"])
        print("URL:", item["url"])
        print("DOMAIN:", item["domain"])
        print("SCORE:", item["score"])
        print(
            "KEYWORDS:",
            ", ".join(item["matched_keywords"])
        )

    # Save processed items
    processed.update(new_ids)

    # Keep state reasonably small
    state["processed"] = list(processed)[-5000:]

    save_state(state)

    print("\nState saved.")
    print("Finished.")


if __name__ == "__main__":
    run_agent()
