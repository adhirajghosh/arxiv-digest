"""Assigns topic clusters to papers based on keyword matching."""
import os
import re
import yaml


TOPICS_PATH = os.path.join(os.path.dirname(__file__), "topics.yaml")

GENERAL_TOPIC = {
    "name": "General",
    "icon": "file-text",
    "color": "#71717a",
    "keywords": [],
}


def load_topics(path: str = TOPICS_PATH) -> list[dict]:
    """Load topic taxonomy from YAML config."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return data["topics"]


def assign_topics(papers: list[dict], topics: list[dict]) -> None:
    """Assign top 1-2 matching topics to each paper (mutates in place).

    Scores each topic by counting keyword hits in title + tldr.
    Assigns top 1-2 topics with score > 0. Falls back to 'General'.
    """
    for paper in papers:
        text = (paper.get("title", "") + " " + paper.get("tldr", "")).lower()
        scored = []
        for topic in topics:
            score = 0
            for keyword in topic["keywords"]:
                if keyword.lower() in text:
                    score += 1
            if score > 0:
                scored.append((score, topic))

        scored.sort(key=lambda x: x[0], reverse=True)

        if scored:
            paper["topics"] = [
                {"name": t["name"], "icon": t["icon"], "color": t["color"]}
                for _, t in scored[:2]
            ]
        else:
            paper["topics"] = [
                {"name": GENERAL_TOPIC["name"], "icon": GENERAL_TOPIC["icon"], "color": GENERAL_TOPIC["color"]}
            ]
