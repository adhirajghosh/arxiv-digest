# tests/test_build.py
import os
import pytest
from build.build_site import build, find_digest_files

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "docs")


def test_find_digest_files():
    files = find_digest_files()
    assert len(files) >= 1
    date_str, path = files[0]
    assert date_str == "2026-04-09"
    assert path.endswith(".txt")


def test_full_build():
    build()
    assert os.path.exists(os.path.join(OUTPUT_DIR, "index.html"))
    assert os.path.exists(os.path.join(OUTPUT_DIR, "2026-04-09.html"))
    assert os.path.exists(os.path.join(OUTPUT_DIR, "static", "style.css"))
    assert os.path.exists(os.path.join(OUTPUT_DIR, "static", "app.js"))

    # Check digest page has expected content
    with open(os.path.join(OUTPUT_DIR, "2026-04-09.html")) as f:
        html = f.read()
    assert "VLMs Need Words" in html
    assert "arXiv Digest" in html
    assert "https://arxiv.org/abs/2604.02486" in html
    assert "topic-pill" in html
    assert "data-topics" in html


def test_index_redirects_to_latest():
    build()
    with open(os.path.join(OUTPUT_DIR, "index.html")) as f:
        html = f.read()
    files = find_digest_files()
    latest_date = max(d for d, _ in files)
    assert f"{latest_date}.html" in html
