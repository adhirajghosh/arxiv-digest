import pytest
from build.parser import parse_digest


MINIMAL_DIGEST = """# arXiv Digest — April 9, 2026

## Top Highlights Today
- **VLMs Need Words** reveals that VLMs systematically fail on visual tasks.

## Papers

### 1. VLMs Need Words: Vision Language Models Ignore Visual Detail
**Authors:** Haz Sameen Shahgir, Xiaofu Chen
**Affiliations:** University of California, Riverside; MBZUAI
**Link:** https://arxiv.org/abs/2604.02486
**Abstract:** Vision Language Models achieve impressive performance across a wide range of multimodal tasks.
**TL;DR:** Demonstrates through controlled experiments that VLMs systematically fail on fine-grained visual perception.
**Take:** This is a genuinely important finding that cleanly isolates a core failure mode.

---

## Overall Trend Today
Today's submissions reveal a maturing field.
"""


def test_parse_date():
    result = parse_digest(MINIMAL_DIGEST, "2026-04-09")
    assert result["date"] == "2026-04-09"
    assert result["date_display"] == "April 9, 2026"


def test_parse_highlights():
    result = parse_digest(MINIMAL_DIGEST, "2026-04-09")
    assert len(result["highlights"]) == 1
    assert result["highlights"][0]["title"] == "VLMs Need Words"
    assert "VLMs systematically fail" in result["highlights"][0]["summary"]


def test_parse_single_paper():
    result = parse_digest(MINIMAL_DIGEST, "2026-04-09")
    assert len(result["papers"]) == 1
    paper = result["papers"][0]
    assert paper["number"] == 1
    assert paper["title"] == "VLMs Need Words: Vision Language Models Ignore Visual Detail"
    assert paper["authors"] == "Haz Sameen Shahgir, Xiaofu Chen"
    assert paper["affiliations"] == "University of California, Riverside; MBZUAI"
    assert paper["arxiv_url"] == "https://arxiv.org/abs/2604.02486"
    assert paper["arxiv_id"] == "2604.02486"
    assert "impressive performance" in paper["abstract"]
    assert "controlled experiments" in paper["tldr"]
    assert "genuinely important" in paper["take"]


def test_parse_overall_trend():
    result = parse_digest(MINIMAL_DIGEST, "2026-04-09")
    assert "maturing field" in result["overall_trend"]


MULTI_PAPER_DIGEST = """# arXiv Digest — April 10, 2026

## Top Highlights Today
- **Paper A** does something cool.
- **Paper B** does something else.

## Papers

### 1. Paper A: First Paper Title
**Authors:** Author One, Author Two
**Affiliations:** University X
**Link:** https://arxiv.org/abs/2604.11111
**Abstract:** Abstract of paper A.
**TL;DR:** TL;DR of paper A.
**Take:** Take on paper A.

---

### 2. Paper B: Second Paper Title
**Authors:** Author Three
**Affiliations:** University Y; University Z
**Link:** https://arxiv.org/abs/2604.22222
**Abstract:** Abstract of paper B.
**TL;DR:** TL;DR of paper B.
**Take:** Take on paper B.

---

## Overall Trend Today
Two papers today covering different areas.
"""


def test_parse_multiple_papers():
    result = parse_digest(MULTI_PAPER_DIGEST, "2026-04-10")
    assert len(result["papers"]) == 2
    assert result["papers"][0]["title"] == "Paper A: First Paper Title"
    assert result["papers"][0]["arxiv_id"] == "2604.11111"
    assert result["papers"][1]["title"] == "Paper B: Second Paper Title"
    assert result["papers"][1]["arxiv_id"] == "2604.22222"


def test_parse_multiple_highlights():
    result = parse_digest(MULTI_PAPER_DIGEST, "2026-04-10")
    assert len(result["highlights"]) == 2
    assert result["highlights"][0]["title"] == "Paper A"
    assert result["highlights"][1]["title"] == "Paper B"
