#!/usr/bin/env python3
"""Build the arXiv Digest static site from .txt digest files."""
import glob
import hashlib
import json
import os
import re
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from build.parser import parse_digest
from build.clusterer import assign_topics, load_topics
from build.icons import svg_icon as _svg_icon_raw


def svg_icon(name: str, size: int = 20, extra_class: str = "") -> Markup:
    """Render an SVG icon as a Jinja2-safe Markup object."""
    return Markup(_svg_icon_raw(name, size, extra_class))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIGEST_DIR = os.path.join(ROOT, "arxiv_digest")
TEMPLATE_DIR = os.path.join(ROOT, "build", "templates")
STATIC_DIR = os.path.join(ROOT, "build", "static")
OUTPUT_DIR = os.path.join(ROOT, "docs")


def find_digest_files() -> list[tuple[str, str]]:
    """Find all .txt digest files and return (date_str, filepath) pairs sorted by date."""
    results = []
    for path in glob.glob(os.path.join(DIGEST_DIR, "**", "*.txt"), recursive=True):
        filename = os.path.basename(path)
        date_match = re.match(r"(\d{4}-\d{2}-\d{2})\.txt$", filename)
        if date_match:
            results.append((date_match.group(1), path))
    results.sort(key=lambda x: x[0])
    return results


def shorten_authors(authors: str, max_count: int = 3) -> tuple[str, bool]:
    """Shorten author list to max_count names + 'et al.'"""
    parts = [a.strip() for a in authors.split(",")]
    if len(parts) <= max_count:
        return authors, False
    return ", ".join(parts[:max_count]) + " et al.", True


def enrich_highlights(highlights: list[dict], papers: list[dict]) -> list[dict]:
    """Match highlights to papers to get topic info and arxiv URLs."""
    enriched = []
    for h in highlights:
        match = None
        for p in papers:
            if h["title"].lower() in p["title"].lower() or p["title"].lower().startswith(h["title"].lower()):
                match = p
                break
        if match and match["topics"]:
            topic = match["topics"][0]
            enriched.append({
                "title": h["title"],
                "summary": h["summary"],
                "color": topic["color"],
                "topic_name": topic["name"],
                "icon_svg": svg_icon(topic["icon"], 14),
                "arxiv_url": match.get("arxiv_url", ""),
            })
        else:
            enriched.append({
                "title": h["title"],
                "summary": h["summary"],
                "color": "#8b5cf6",
                "topic_name": "General",
                "icon_svg": svg_icon("file-text", 14),
                "arxiv_url": "",
            })
    return enriched


def build_topic_summary(papers: list[dict]) -> list[dict]:
    """Build topic summary with counts for the filter bar."""
    topic_counts: dict[str, dict] = {}
    for paper in papers:
        for t in paper.get("topics", []):
            name = t["name"]
            if name not in topic_counts:
                topic_counts[name] = {
                    "name": name,
                    "color": t["color"],
                    "icon": t.get("icon", "file-text"),
                    "icon_svg": svg_icon(t.get("icon", "file-text"), 14),
                    "count": 0,
                }
            topic_counts[name]["count"] += 1
    return sorted(topic_counts.values(), key=lambda x: x["count"], reverse=True)


def prepare_paper_data(papers: list[dict]) -> list[dict]:
    """Add display-ready fields to paper dicts."""
    for paper in papers:
        short, has_more = shorten_authors(paper.get("authors", ""))
        paper["authors_short"] = short
        paper["has_more_authors"] = has_more
        paper["topic_names_json"] = json.dumps([t["name"] for t in paper.get("topics", [])])
        for t in paper.get("topics", []):
            t["icon_svg"] = svg_icon(t.get("icon", "file-text"), 12)
    return papers


def _compute_build_version() -> str:
    """Short hash of static assets so <link>/<script> tags bust browser cache."""
    h = hashlib.sha256()
    for name in ("style.css", "app.js"):
        path = os.path.join(STATIC_DIR, name)
        if os.path.exists(path):
            with open(path, "rb") as f:
                h.update(f.read())
    return h.hexdigest()[:8]


def build():
    """Main build entry point."""
    # Setup output directory. Preserve superpowers/ docs and any dotfiles
    # like .nojekyll that configure GitHub Pages.
    PRESERVE = {"superpowers", ".nojekyll", "CNAME"}
    if os.path.exists(OUTPUT_DIR):
        for item in os.listdir(OUTPUT_DIR):
            if item in PRESERVE:
                continue
            path = os.path.join(OUTPUT_DIR, item)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Ensure .nojekyll exists so GitHub Pages serves files as-is.
    nojekyll = os.path.join(OUTPUT_DIR, ".nojekyll")
    if not os.path.exists(nojekyll):
        open(nojekyll, "w").close()

    # Copy static assets
    static_out = os.path.join(OUTPUT_DIR, "static")
    if os.path.exists(static_out):
        shutil.rmtree(static_out)
    shutil.copytree(STATIC_DIR, static_out)

    # Cache-busting version derived from static asset contents
    build_version = _compute_build_version()

    # Load topics
    topics = load_topics()

    # Find and parse all digests
    digest_files = find_digest_files()
    if not digest_files:
        print("No digest files found.")
        return

    digests = []
    for date_str, filepath in digest_files:
        with open(filepath) as f:
            text = f.read()
        digest = parse_digest(text, date_str)
        assign_topics(digest["papers"], topics)
        digests.append(digest)

    # Sort newest first
    digests.sort(key=lambda d: d["date"], reverse=True)

    # All dates for navigation
    all_dates = [{"date": d["date"], "date_display": d["date_display"]} for d in digests]
    all_dates_json = json.dumps([d["date"] for d in digests])

    # Setup Jinja2
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html"]),
    )

    # Common template variables
    common_icons = {
        "sparkle_icon": svg_icon("sparkles", 24),
        "trend_icon": svg_icon("trend", 18),
        "external_link_icon": svg_icon("external-link", 14),
        "chevron_left_icon": svg_icon("chevron-left", 20),
        "chevron_right_icon": svg_icon("chevron-right", 20),
        "chevron_down_icon": svg_icon("chevron-down", 14),
        "calendar_icon": svg_icon("calendar", 16),
        "search_icon": svg_icon("search", 20),
        "sun_icon": svg_icon("sun", 20),
        "moon_icon": svg_icon("moon", 20),
        "x_icon": svg_icon("x", 20),
    }

    # Render each digest page
    digest_template = env.get_template("digest.html")
    for i, digest in enumerate(digests):
        prev_date = digests[i + 1]["date"] if i + 1 < len(digests) else None
        next_date = digests[i - 1]["date"] if i > 0 else None

        papers = prepare_paper_data(digest["papers"])
        highlights = enrich_highlights(digest["highlights"], papers)
        topic_summary = build_topic_summary(papers)

        html = digest_template.render(
            date_display=digest["date_display"],
            current_date=digest["date"],
            prev_date=prev_date,
            next_date=next_date,
            all_dates=all_dates,
            all_dates_json=all_dates_json,
            highlights=highlights,
            overall_trend=digest["overall_trend"],
            topic_summary=topic_summary,
            papers=papers,
            build_version=build_version,
            **common_icons,
        )

        output_path = os.path.join(OUTPUT_DIR, f"{digest['date']}.html")
        with open(output_path, "w") as f:
            f.write(html)
        print(f"Built: {digest['date']}.html ({len(papers)} papers)")

    # Render index redirect
    index_template = env.get_template("index.html")
    index_html = index_template.render(latest_date=digests[0]["date"])
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as f:
        f.write(index_html)
    print(f"Built: index.html -> {digests[0]['date']}.html")


if __name__ == "__main__":
    build()
