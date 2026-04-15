# arXiv Digest Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static website generator that converts plain-text arXiv digests into an aesthetic, topic-clustered website hosted on GitHub Pages.

**Architecture:** Python build script parses `.txt` digest files, assigns topic clusters via keyword matching, and renders Jinja2 templates into static HTML served from `docs/`. GitHub Action auto-rebuilds on push.

**Tech Stack:** Python 3.11, Jinja2, PyYAML, pytest, vanilla CSS/JS, GitHub Actions

**Spec:** `docs/superpowers/specs/2026-04-15-arxiv-digest-website-design.md`

---

## File Structure

```
arxiv-digest/
├── build/
│   ├── __init__.py
│   ├── parser.py              # Parses .txt digest files into structured dicts
│   ├── clusterer.py           # Assigns topic clusters to papers
│   ├── build_site.py          # Main build orchestrator
│   ├── topics.yaml            # Topic taxonomy config
│   ├── icons.py               # SVG icon path data for all icons
│   ├── templates/
│   │   ├── base.html          # Shared layout (head, header, footer)
│   │   ├── digest.html        # Per-date digest page
│   │   └── index.html         # Redirect page to latest digest
│   └── static/
│       ├── style.css          # All styles (dark/light, responsive, animations)
│       └── app.js             # Client-side interactivity
├── tests/
│   ├── __init__.py
│   ├── test_parser.py         # Parser unit tests
│   ├── test_clusterer.py      # Clusterer unit tests
│   └── test_build.py          # Integration test for full build
├── docs/                      # Generated output (committed)
│   ├── index.html
│   ├── static/
│   │   ├── style.css
│   │   └── app.js
│   └── 2026-04-09.html
├── .github/
│   └── workflows/
│       └── build.yml
└── requirements.txt
```

---

### Task 1: Project Setup and Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `build/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
jinja2>=3.1
pyyaml>=6.0
pytest>=8.0
```

- [ ] **Step 2: Create package init files**

Create empty `build/__init__.py` and `tests/__init__.py`.

- [ ] **Step 3: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: All packages install successfully.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt build/__init__.py tests/__init__.py
git commit -m "feat: project setup with dependencies"
```

---

### Task 2: Digest Parser — Tests

**Files:**
- Create: `tests/test_parser.py`

The parser must handle the exact format in `arxiv_digest/april_26/2026-04-09.txt`. Key patterns:
- `# arXiv Digest — April 9, 2026` (title with date)
- `## Top Highlights Today` followed by `- **Title** summary` bullets
- `### N. Paper Title` for each paper
- `**Authors:** ...`, `**Affiliations:** ...`, `**Link:** ...`, `**Abstract:** ...`, `**TL;DR:** ...`, `**Take:** ...` fields
- `---` separators between papers
- `## Overall Trend Today` followed by paragraph text

- [ ] **Step 1: Write test for parsing date from header**

```python
# tests/test_parser.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /tmp/arxiv-digest && python -m pytest tests/test_parser.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'build.parser'`

- [ ] **Step 3: Commit**

```bash
git add tests/test_parser.py
git commit -m "test: add parser unit tests"
```

---

### Task 3: Digest Parser — Implementation

**Files:**
- Create: `build/parser.py`

- [ ] **Step 1: Implement parse_digest function**

```python
# build/parser.py
"""Parses arXiv digest .txt files into structured data."""
import re


def parse_digest(text: str, date_str: str) -> dict:
    """Parse a digest text file into structured data.

    Args:
        text: Raw text content of the digest file.
        date_str: Date string in YYYY-MM-DD format (from filename).

    Returns:
        Dict with keys: date, date_display, highlights, papers, overall_trend.
    """
    date_display = _extract_date_display(text)
    highlights = _extract_highlights(text)
    papers = _extract_papers(text)
    overall_trend = _extract_overall_trend(text)

    return {
        "date": date_str,
        "date_display": date_display,
        "highlights": highlights,
        "papers": papers,
        "overall_trend": overall_trend,
    }


def _extract_date_display(text: str) -> str:
    """Extract display date from the '# arXiv Digest — April 9, 2026' header."""
    match = re.search(r"^# arXiv Digest\s*[—–-]\s*(.+)$", text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def _extract_highlights(text: str) -> list[dict]:
    """Extract top highlights from bullet list under '## Top Highlights Today'."""
    highlights = []
    section = _extract_section(text, "Top Highlights Today")
    if not section:
        return highlights

    for match in re.finditer(r"-\s+\*\*(.+?)\*\*\s+(.+?)(?:\n|$)", section):
        highlights.append({
            "title": match.group(1).strip(),
            "summary": match.group(2).strip(),
        })
    return highlights


def _extract_papers(text: str) -> list[dict]:
    """Extract all papers from the '## Papers' section."""
    papers_section = _extract_section(text, "Papers")
    if not papers_section:
        return []

    # Split on paper headers: ### N. Title
    paper_blocks = re.split(r"(?=^### \d+\.)", papers_section, flags=re.MULTILINE)
    papers = []
    for block in paper_blocks:
        block = block.strip()
        if not block.startswith("### "):
            continue
        paper = _parse_paper_block(block)
        if paper:
            papers.append(paper)
    return papers


def _parse_paper_block(block: str) -> dict | None:
    """Parse a single paper block into a dict."""
    # Title: ### N. Title
    title_match = re.match(r"### (\d+)\.\s+(.+?)$", block, re.MULTILINE)
    if not title_match:
        return None

    number = int(title_match.group(1))
    title = title_match.group(2).strip()

    def extract_field(name: str) -> str:
        pattern = rf"\*\*{name}:\*\*\s+(.+?)(?=\n\*\*[A-Z]|\n---|\Z)"
        match = re.search(pattern, block, re.DOTALL)
        return match.group(1).strip() if match else ""

    authors = extract_field("Authors")
    affiliations = extract_field("Affiliations")
    link = extract_field("Link")
    abstract = extract_field("Abstract")
    tldr = extract_field("TL;DR")
    take = extract_field("Take")

    arxiv_id = ""
    id_match = re.search(r"arxiv\.org/abs/(\S+)", link)
    if id_match:
        arxiv_id = id_match.group(1)

    return {
        "number": number,
        "title": title,
        "authors": authors,
        "affiliations": affiliations,
        "arxiv_url": link,
        "arxiv_id": arxiv_id,
        "abstract": abstract,
        "tldr": tldr,
        "take": take,
        "topics": [],  # Filled in by clusterer
    }


def _extract_overall_trend(text: str) -> str:
    """Extract the overall trend section text."""
    return _extract_section(text, "Overall Trend Today").strip()


def _extract_section(text: str, heading: str) -> str:
    """Extract text between a ## heading and the next ## heading (or end)."""
    pattern = rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `cd /tmp/arxiv-digest && python -m pytest tests/test_parser.py -v`
Expected: All 6 tests PASS.

- [ ] **Step 3: Run parser against the real digest file as a sanity check**

Run: `cd /tmp/arxiv-digest && python -c "from build.parser import parse_digest; import json; text = open('arxiv_digest/april_26/2026-04-09.txt').read(); result = parse_digest(text, '2026-04-09'); print(f'Papers: {len(result[\"papers\"])}, Highlights: {len(result[\"highlights\"])}'); print(f'First paper: {result[\"papers\"][0][\"title\"][:60]}...')"`
Expected: `Papers: 13, Highlights: 5, First paper: VLMs Need Words...`

- [ ] **Step 4: Commit**

```bash
git add build/parser.py
git commit -m "feat: implement digest parser"
```

---

### Task 4: Topic Clusterer — Tests

**Files:**
- Create: `tests/test_clusterer.py`

- [ ] **Step 1: Write clusterer tests**

```python
# tests/test_clusterer.py
import pytest
from build.clusterer import assign_topics, load_topics


def test_load_topics():
    topics = load_topics()
    assert len(topics) >= 10
    assert any(t["name"] == "Hallucination" for t in topics)
    for t in topics:
        assert "name" in t
        assert "keywords" in t
        assert "color" in t
        assert "icon" in t


def test_assign_hallucination_topic():
    topics = load_topics()
    paper = {
        "title": "Focus Matters: Phase-Aware Suppression for Hallucination in VLMs",
        "tldr": "Discovers a three-phase attention pattern and shows hallucinations are linked to low-attention tokens.",
        "topics": [],
    }
    assign_topics([paper], topics)
    topic_names = [t["name"] for t in paper["topics"]]
    assert "Hallucination" in topic_names


def test_assign_video_topic():
    topics = load_topics()
    paper = {
        "title": "VideoZeroBench: Probing the Limits of Video MLLMs",
        "tldr": "Introduces a benchmark where video MLLMs must provide temporal intervals and spatial bounding boxes.",
        "topics": [],
    }
    assign_topics([paper], topics)
    topic_names = [t["name"] for t in paper["topics"]]
    assert "Video Understanding" in topic_names


def test_assign_max_two_topics():
    topics = load_topics()
    paper = {
        "title": "Video benchmark evaluation for hallucination in streaming multimodal VLM architecture",
        "tldr": "Video benchmark evaluation hallucination streaming VLM architecture training distillation 3D spatial multilingual reasoning robustness attention",
        "topics": [],
    }
    assign_topics([paper], topics)
    assert len(paper["topics"]) <= 2


def test_assign_general_when_no_match():
    topics = load_topics()
    paper = {
        "title": "Quantum Computing for Protein Folding",
        "tldr": "Uses quantum annealing to predict protein structures.",
        "topics": [],
    }
    assign_topics([paper], topics)
    assert len(paper["topics"]) == 1
    assert paper["topics"][0]["name"] == "General"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /tmp/arxiv-digest && python -m pytest tests/test_clusterer.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'build.clusterer'`

- [ ] **Step 3: Commit**

```bash
git add tests/test_clusterer.py
git commit -m "test: add clusterer unit tests"
```

---

### Task 5: Topic Taxonomy Config + Clusterer Implementation

**Files:**
- Create: `build/topics.yaml`
- Create: `build/clusterer.py`

- [ ] **Step 1: Create topics.yaml**

```yaml
# build/topics.yaml
topics:
  - name: "VLM Architecture"
    icon: "brain-circuit"
    color: "#8b5cf6"
    keywords:
      - "VLM"
      - "vision-language"
      - "multimodal model"
      - "unified model"
      - "architecture"
      - "latent space"
      - "MLLM"
      - "vision language model"

  - name: "Hallucination"
    icon: "eye-off"
    color: "#f59e0b"
    keywords:
      - "hallucination"
      - "hallucinate"
      - "faithfulness"
      - "grounding"
      - "unfaithful"

  - name: "Video Understanding"
    icon: "film"
    color: "#10b981"
    keywords:
      - "video"
      - "temporal"
      - "VideoLLM"
      - "video understanding"
      - "video QA"
      - "spatio-temporal"

  - name: "Benchmarks & Evaluation"
    icon: "bar-chart-3"
    color: "#06b6d4"
    keywords:
      - "benchmark"
      - "evaluation"
      - "eval"
      - "dataset"
      - "annotation"
      - "leaderboard"

  - name: "3D & Spatial"
    icon: "box"
    color: "#ec4899"
    keywords:
      - "3D"
      - "spatial"
      - "multi-view"
      - "depth"
      - "geometry"
      - "consistency"

  - name: "Training & Distillation"
    icon: "zap"
    color: "#f97316"
    keywords:
      - "distillation"
      - "fine-tuning"
      - "SFT"
      - "RLHF"
      - "pretraining"
      - "reinforcement learning"
      - "GRPO"
      - "alignment"

  - name: "Generation"
    icon: "palette"
    color: "#a855f7"
    keywords:
      - "generation"
      - "generative"
      - "image generation"
      - "video generation"
      - "text-to-image"
      - "text-to-video"

  - name: "Streaming & Real-time"
    icon: "radio"
    color: "#14b8a6"
    keywords:
      - "streaming"
      - "real-time"
      - "always-on"
      - "live"
      - "deployment"
      - "inference speed"

  - name: "Multilingual"
    icon: "globe"
    color: "#6366f1"
    keywords:
      - "Japanese"
      - "multilingual"
      - "non-English"
      - "cross-lingual"
      - "Chinese"

  - name: "Reasoning"
    icon: "git-branch"
    color: "#eab308"
    keywords:
      - "reasoning"
      - "chain-of-thought"
      - "planning"
      - "logic"
      - "step-by-step"

  - name: "Robustness"
    icon: "shield"
    color: "#ef4444"
    keywords:
      - "degraded"
      - "robust"
      - "noisy"
      - "corruption"
      - "adversarial"
      - "blur"
      - "compression"

  - name: "Attention & Interpretability"
    icon: "scan-eye"
    color: "#84cc16"
    keywords:
      - "attention"
      - "interpretability"
      - "explainability"
      - "evidence"
      - "saliency"

  - name: "Infrastructure & Tooling"
    icon: "wrench"
    color: "#78716c"
    keywords:
      - "framework"
      - "infrastructure"
      - "tooling"
      - "library"
      - "open-source"
      - "ecosystem"

  - name: "Diffusion Models"
    icon: "sparkles"
    color: "#d946ef"
    keywords:
      - "diffusion"
      - "denoising"
      - "score matching"
      - "DDPM"
      - "flow matching"
      - "dLLM"
```

- [ ] **Step 2: Implement clusterer.py**

```python
# build/clusterer.py
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
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `cd /tmp/arxiv-digest && python -m pytest tests/test_clusterer.py -v`
Expected: All 5 tests PASS.

- [ ] **Step 4: Commit**

```bash
git add build/topics.yaml build/clusterer.py
git commit -m "feat: implement topic clusterer with keyword taxonomy"
```

---

### Task 6: SVG Icons Module

**Files:**
- Create: `build/icons.py`

This module stores inline SVG path data for all topic icons and UI icons. Using Lucide icon paths (MIT licensed, 24x24 viewBox).

- [ ] **Step 1: Create icons.py with all icon SVGs**

```python
# build/icons.py
"""Inline SVG icons from Lucide (https://lucide.dev). MIT licensed, 24x24 viewBox."""

# Map of icon name -> SVG inner content (paths/shapes, no wrapper <svg> tag)
ICONS = {
    # Topic icons
    "brain-circuit": '<path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M19.938 10.5a4 4 0 0 1 .585.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M19.967 17.484A4 4 0 0 1 18 18"/>',
    "eye-off": '<path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/><path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/><path d="m2 2 20 20"/>',
    "film": '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M7 3v18"/><path d="M17 3v18"/><path d="M3 7h4"/><path d="M3 11h4"/><path d="M3 15h4"/><path d="M17 7h4"/><path d="M17 11h4"/><path d="M17 15h4"/>',
    "bar-chart-3": '<path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="M7 16h.01"/><path d="M11 12h.01"/><path d="M15 16h.01"/><path d="M19 8h.01"/>',
    "box": '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "zap": '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
    "palette": '<circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>',
    "radio": '<path d="M4.9 19.1C1 15.2 1 8.8 4.9 4.9"/><path d="M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5"/><circle cx="12" cy="12" r="2"/><path d="M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5"/><path d="M19.1 4.9C23 8.8 23 15.1 19.1 19"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "git-branch": '<line x1="6" x2="6" y1="3" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    "scan-eye": '<path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><circle cx="12" cy="12" r="1"/><path d="M18.944 12.33a1 1 0 0 0 0-.66 7.5 7.5 0 0 0-13.888 0 1 1 0 0 0 0 .66 7.5 7.5 0 0 0 13.888 0"/>',
    "wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "sparkles": '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/>',
    "file-text": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',

    # UI icons
    "external-link": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
    "moon": '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    "chevron-left": '<path d="m15 18-6-6 6-6"/>',
    "chevron-right": '<path d="m9 18 6-6-6-6"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "chevron-up": '<path d="m18 15-6-6-6 6"/>',
    "calendar": '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "trend": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
}


def svg_icon(name: str, size: int = 20, extra_class: str = "") -> str:
    """Render an SVG icon by name.

    Args:
        name: Icon name from ICONS dict.
        size: Width and height in pixels.
        extra_class: Additional CSS class to apply.

    Returns:
        Complete <svg> element as a string.
    """
    paths = ICONS.get(name, ICONS["file-text"])
    cls = f' class="{extra_class}"' if extra_class else ""
    return (
        f'<svg{cls} xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{paths}</svg>'
    )
```

- [ ] **Step 2: Quick verify icons render valid SVG**

Run: `cd /tmp/arxiv-digest && python -c "from build.icons import svg_icon; print(svg_icon('brain-circuit', 24)[:80])"`
Expected: Starts with `<svg xmlns=...`

- [ ] **Step 3: Commit**

```bash
git add build/icons.py
git commit -m "feat: add SVG icon module with Lucide icons"
```

---

### Task 7: Jinja2 Templates — Base Layout and Index Redirect

**Files:**
- Create: `build/templates/base.html`
- Create: `build/templates/index.html`

- [ ] **Step 1: Create base.html template**

This is the shared layout with header, footer, CSS/JS includes, and theme toggle. The full file content follows (long — this is the main template shell):

```html
{# build/templates/base.html #}
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}arXiv Digest{% endblock %}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="static/style.css">
</head>
<body>
    <header class="header" id="header">
        <div class="header-inner">
            <a href="index.html" class="logo">
                {{ sparkle_icon }} <span>arXiv Digest</span>
            </a>
            <nav class="date-nav" aria-label="Date navigation">
                {% if prev_date %}
                <a href="{{ prev_date }}.html" class="nav-btn" aria-label="Previous digest">{{ chevron_left_icon }}</a>
                {% else %}
                <span class="nav-btn disabled">{{ chevron_left_icon }}</span>
                {% endif %}
                <div class="date-selector">
                    <button class="date-btn" id="date-toggle">
                        {{ calendar_icon }}
                        <span>{{ date_display }}</span>
                        {{ chevron_down_icon }}
                    </button>
                    <div class="date-dropdown" id="date-dropdown">
                        {% for d in all_dates %}
                        <a href="{{ d.date }}.html" class="date-option{% if d.date == current_date %} active{% endif %}">{{ d.date_display }}</a>
                        {% endfor %}
                    </div>
                </div>
                {% if next_date %}
                <a href="{{ next_date }}.html" class="nav-btn" aria-label="Next digest">{{ chevron_right_icon }}</a>
                {% else %}
                <span class="nav-btn disabled">{{ chevron_right_icon }}</span>
                {% endif %}
            </nav>
            <div class="header-actions">
                <button class="icon-btn" id="search-toggle" aria-label="Search">{{ search_icon }}</button>
                <button class="icon-btn" id="theme-toggle" aria-label="Toggle theme">
                    <span class="theme-icon-sun">{{ sun_icon }}</span>
                    <span class="theme-icon-moon">{{ moon_icon }}</span>
                </button>
            </div>
        </div>
        <div class="search-bar" id="search-bar">
            <input type="text" id="search-input" placeholder="Search papers..." autocomplete="off">
            <button class="icon-btn" id="search-close" aria-label="Close search">{{ x_icon }}</button>
        </div>
    </header>

    <main class="main">
        {% block content %}{% endblock %}
    </main>

    <footer class="footer">
        <p>Papers sourced from <a href="https://arxiv.org" target="_blank" rel="noopener">arXiv.org</a></p>
        <p><a href="https://github.com/adhirajghosh/arxiv-digest" target="_blank" rel="noopener">GitHub</a></p>
    </footer>

    <script src="static/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create index.html redirect template**

```html
{# build/templates/index.html #}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url={{ latest_date }}.html">
    <title>arXiv Digest</title>
</head>
<body>
    <p>Redirecting to <a href="{{ latest_date }}.html">latest digest</a>...</p>
</body>
</html>
```

- [ ] **Step 3: Commit**

```bash
git add build/templates/base.html build/templates/index.html
git commit -m "feat: add base layout and index redirect templates"
```

---

### Task 8: Jinja2 Template — Digest Page

**Files:**
- Create: `build/templates/digest.html`

This is the main content template that renders highlights, trend, topic filter bar, and paper cards.

- [ ] **Step 1: Create digest.html**

```html
{# build/templates/digest.html #}
{% extends "base.html" %}
{% block title %}arXiv Digest — {{ date_display }}{% endblock %}

{% block content %}
{# ── Hero: Top Highlights ── #}
<section class="highlights-section">
    <h2 class="section-title">{{ sparkle_icon }} Top Highlights</h2>
    <div class="highlights-row">
        {% for h in highlights %}
        <div class="highlight-card" style="--topic-color: {{ h.color }}">
            <div class="highlight-topic">{{ h.icon_svg }} <span>{{ h.topic_name }}</span></div>
            <h3 class="highlight-title">
                {% if h.arxiv_url %}<a href="{{ h.arxiv_url }}" target="_blank" rel="noopener">{{ h.title }}</a>{% else %}{{ h.title }}{% endif %}
            </h3>
            <p class="highlight-summary">{{ h.summary }}</p>
        </div>
        {% endfor %}
    </div>
</section>

{# ── Daily Trend ── #}
{% if overall_trend %}
<section class="trend-section">
    <div class="trend-card">
        <h2 class="trend-label">{{ trend_icon }} Today's Trend</h2>
        <p class="trend-text">{{ overall_trend }}</p>
    </div>
</section>
{% endif %}

{# ── Topic Filter Bar ── #}
<section class="filter-section" id="filter-bar">
    <div class="filter-row">
        <button class="topic-pill active" data-topic="all">
            All <span class="pill-count">{{ papers|length }}</span>
        </button>
        {% for topic in topic_summary %}
        <button class="topic-pill" data-topic="{{ topic.name }}" style="--pill-color: {{ topic.color }}">
            {{ topic.icon_svg }} {{ topic.name }} <span class="pill-count">{{ topic.count }}</span>
        </button>
        {% endfor %}
    </div>
</section>

{# ── Paper Cards Grid ── #}
<section class="papers-section">
    <div class="papers-grid">
        {% for paper in papers %}
        <article class="paper-card" data-topics="{{ paper.topic_names_json }}" style="--card-accent: {{ paper.topics[0].color }}">
            <div class="paper-header">
                <div class="paper-topics">
                    {% for t in paper.topics %}
                    <span class="paper-topic-pill" style="--pill-color: {{ t.color }}">{{ t.icon_svg }} {{ t.name }}</span>
                    {% endfor %}
                </div>
                <span class="paper-number">#{{ paper.number }}</span>
            </div>

            <h3 class="paper-title">
                <a href="{{ paper.arxiv_url }}" target="_blank" rel="noopener">{{ paper.title }} {{ external_link_icon }}</a>
            </h3>

            <p class="paper-authors">{{ paper.authors_short }}{% if paper.has_more_authors %} <button class="expand-authors" aria-label="Show all authors">+more</button>{% endif %}</p>
            <p class="paper-authors-full hidden">{{ paper.authors }}</p>
            <p class="paper-affiliations">{{ paper.affiliations }}</p>

            <div class="paper-tldr">
                <h4>TL;DR</h4>
                <p>{{ paper.tldr }}</p>
            </div>

            <div class="paper-expandable">
                <button class="expand-btn" data-target="take-{{ paper.number }}">Show take {{ chevron_down_icon }}</button>
                <div class="expandable-content" id="take-{{ paper.number }}">
                    <p>{{ paper.take }}</p>
                </div>
            </div>

            <div class="paper-expandable">
                <button class="expand-btn" data-target="abstract-{{ paper.number }}">Show abstract {{ chevron_down_icon }}</button>
                <div class="expandable-content" id="abstract-{{ paper.number }}">
                    <p>{{ paper.abstract }}</p>
                </div>
            </div>

            <div class="paper-footer">
                <a href="{{ paper.arxiv_url }}" target="_blank" rel="noopener" class="arxiv-btn">
                    {{ external_link_icon }} <code>{{ paper.arxiv_id }}</code>
                </a>
            </div>
        </article>
        {% endfor %}
    </div>
</section>
{% endblock %}
```

- [ ] **Step 2: Commit**

```bash
git add build/templates/digest.html
git commit -m "feat: add digest page template with highlights, trend, and paper cards"
```

---

### Task 9: CSS Stylesheet

**Files:**
- Create: `build/static/style.css`

- [ ] **Step 1: Create style.css with full dark/light theme, responsive grid, and animations**

This is the largest single file. The complete CSS follows. Key design principles:
- CSS custom properties for theming
- Dark mode default, light mode via `[data-theme="light"]`
- 2-column grid at >= 768px
- Smooth transitions on filter, expand, scroll-in
- Glassmorphism header with backdrop blur
- Topic pills with per-topic colors via `--pill-color`
- Card left-border accent via `--card-accent`

```css
/* build/static/style.css */

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #0f0f17;
    --bg-card: #13131a;
    --bg-card-hover: #1a1a24;
    --border-subtle: rgba(255,255,255,0.06);
    --border-medium: rgba(255,255,255,0.1);
    --text-primary: #e4e4e7;
    --text-secondary: #a1a1aa;
    --text-muted: #71717a;
    --accent: #8b5cf6;
    --accent-hover: #7c3aed;
    --accent-glow: rgba(139,92,246,0.15);
    --radius: 12px;
    --radius-sm: 8px;
    --radius-pill: 100px;
    --shadow: 0 4px 24px rgba(0,0,0,0.3);
    --shadow-hover: 0 8px 32px rgba(0,0,0,0.4);
    --transition: 0.2s ease;
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', ui-monospace, monospace;
}

[data-theme="light"] {
    --bg-primary: #f8f8fc;
    --bg-secondary: #f0f0f6;
    --bg-card: #ffffff;
    --bg-card-hover: #f4f4f8;
    --border-subtle: rgba(0,0,0,0.07);
    --border-medium: rgba(0,0,0,0.12);
    --text-primary: #18181b;
    --text-secondary: #52525b;
    --text-muted: #a1a1aa;
    --accent: #7c3aed;
    --accent-hover: #6d28d9;
    --accent-glow: rgba(124,58,237,0.1);
    --shadow: 0 4px 24px rgba(0,0,0,0.06);
    --shadow-hover: 0 8px 32px rgba(0,0,0,0.1);
}

html { scroll-behavior: smooth; }

body {
    font-family: var(--font-sans);
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    font-size: 16px;
    min-height: 100vh;
}

a { color: var(--accent); text-decoration: none; transition: color var(--transition); }
a:hover { color: var(--accent-hover); }

code { font-family: var(--font-mono); font-size: 0.85em; }

/* ── Header ── */
.header {
    position: sticky;
    top: 0;
    z-index: 100;
    background: color-mix(in srgb, var(--bg-primary) 80%, transparent);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--border-subtle);
}

.header-inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0.75rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}

.logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
    text-decoration: none;
    white-space: nowrap;
}

.logo span {
    background: linear-gradient(135deg, var(--accent), #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.logo svg { color: var(--accent); }

.date-nav {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.nav-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: var(--radius-sm);
    color: var(--text-secondary);
    transition: all var(--transition);
    text-decoration: none;
}

.nav-btn:hover:not(.disabled) { background: var(--border-subtle); color: var(--text-primary); }
.nav-btn.disabled { opacity: 0.3; cursor: default; }

.date-selector { position: relative; }

.date-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    background: transparent;
    color: var(--text-primary);
    font-family: var(--font-sans);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition);
}

.date-btn:hover { border-color: var(--border-medium); background: var(--bg-card); }
.date-btn svg { width: 16px; height: 16px; color: var(--text-muted); }

.date-dropdown {
    display: none;
    position: absolute;
    top: calc(100% + 4px);
    left: 50%;
    transform: translateX(-50%);
    min-width: 200px;
    max-height: 300px;
    overflow-y: auto;
    background: var(--bg-card);
    border: 1px solid var(--border-medium);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    z-index: 200;
}

.date-dropdown.open { display: block; }

.date-option {
    display: block;
    padding: 0.5rem 1rem;
    color: var(--text-secondary);
    font-size: 0.875rem;
    transition: all var(--transition);
}

.date-option:hover { background: var(--accent-glow); color: var(--text-primary); }
.date-option.active { color: var(--accent); font-weight: 600; }

.header-actions { display: flex; gap: 0.25rem; }

.icon-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border: none;
    border-radius: var(--radius-sm);
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all var(--transition);
}

.icon-btn:hover { background: var(--border-subtle); color: var(--text-primary); }
.icon-btn svg { width: 20px; height: 20px; }

/* Theme toggle */
[data-theme="dark"] .theme-icon-sun { display: none; }
[data-theme="dark"] .theme-icon-moon { display: flex; }
[data-theme="light"] .theme-icon-sun { display: flex; }
[data-theme="light"] .theme-icon-moon { display: none; }
.theme-icon-sun, .theme-icon-moon { display: flex; align-items: center; }

/* Search bar */
.search-bar {
    display: none;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1.5rem 0.75rem;
    gap: 0.5rem;
    align-items: center;
}

.search-bar.open { display: flex; }

.search-bar input {
    flex: 1;
    padding: 0.625rem 1rem;
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-sm);
    background: var(--bg-card);
    color: var(--text-primary);
    font-family: var(--font-sans);
    font-size: 0.9rem;
    outline: none;
    transition: border-color var(--transition);
}

.search-bar input:focus { border-color: var(--accent); }
.search-bar input::placeholder { color: var(--text-muted); }

/* ── Main ── */
.main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
}

/* ── Highlights Section ── */
.section-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: var(--text-primary);
}

.section-title svg { color: var(--accent); width: 24px; height: 24px; }

.highlights-row {
    display: flex;
    gap: 1rem;
    overflow-x: auto;
    padding-bottom: 0.5rem;
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
}

.highlights-row::-webkit-scrollbar { height: 4px; }
.highlights-row::-webkit-scrollbar-track { background: transparent; }
.highlights-row::-webkit-scrollbar-thumb { background: var(--border-medium); border-radius: 2px; }

.highlight-card {
    flex: 0 0 280px;
    scroll-snap-align: start;
    padding: 1.25rem;
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--topic-color, var(--accent));
    border-radius: var(--radius);
    transition: all var(--transition);
}

.highlight-card:hover { background: var(--bg-card-hover); box-shadow: var(--shadow); transform: translateY(-2px); }

.highlight-topic {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--topic-color, var(--accent));
    margin-bottom: 0.5rem;
}

.highlight-topic svg { width: 14px; height: 14px; }

.highlight-title {
    font-size: 0.95rem;
    font-weight: 600;
    line-height: 1.4;
    margin-bottom: 0.5rem;
}

.highlight-title a { color: var(--text-primary); }
.highlight-title a:hover { color: var(--accent); }

.highlight-summary {
    font-size: 0.8rem;
    color: var(--text-secondary);
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* ── Trend Section ── */
.trend-section { margin: 2rem 0; }

.trend-card {
    padding: 1.5rem;
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius);
    position: relative;
    overflow: hidden;
}

.trend-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), #ec4899, #f59e0b);
}

.trend-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--accent);
    margin-bottom: 0.75rem;
}

.trend-label svg { width: 18px; height: 18px; }

.trend-text {
    font-size: 0.925rem;
    color: var(--text-secondary);
    line-height: 1.7;
}

/* ── Filter Section ── */
.filter-section {
    position: sticky;
    top: 60px;
    z-index: 50;
    background: color-mix(in srgb, var(--bg-primary) 85%, transparent);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    margin: 0 -1.5rem;
    padding: 0.75rem 1.5rem;
    border-bottom: 1px solid var(--border-subtle);
}

.filter-row {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    padding-bottom: 0.25rem;
    -webkit-overflow-scrolling: touch;
}

.filter-row::-webkit-scrollbar { height: 0; }

.topic-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0.75rem;
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-pill);
    background: transparent;
    color: var(--text-secondary);
    font-family: var(--font-sans);
    font-size: 0.8rem;
    font-weight: 500;
    white-space: nowrap;
    cursor: pointer;
    transition: all var(--transition);
}

.topic-pill svg { width: 14px; height: 14px; }

.topic-pill:hover {
    border-color: var(--pill-color, var(--accent));
    color: var(--pill-color, var(--accent));
    background: color-mix(in srgb, var(--pill-color, var(--accent)) 10%, transparent);
}

.topic-pill.active {
    background: var(--pill-color, var(--accent));
    border-color: var(--pill-color, var(--accent));
    color: #fff;
}

.pill-count {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 20px;
    height: 20px;
    padding: 0 6px;
    border-radius: 10px;
    background: var(--border-subtle);
    font-size: 0.7rem;
    font-weight: 600;
}

.topic-pill.active .pill-count { background: rgba(255,255,255,0.2); }

/* ── Papers Grid ── */
.papers-section { margin-top: 2rem; }

.papers-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.25rem;
}

@media (min-width: 768px) {
    .papers-grid { grid-template-columns: repeat(2, 1fr); }
}

.paper-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--card-accent, var(--accent));
    border-radius: var(--radius);
    padding: 1.5rem;
    transition: all 0.3s ease;
    opacity: 1;
    transform: translateY(0);
}

.paper-card:hover { background: var(--bg-card-hover); box-shadow: var(--shadow-hover); transform: translateY(-2px); }

.paper-card[data-hidden="true"] {
    display: none;
}

.paper-card.fade-in {
    animation: fadeSlideIn 0.4s ease forwards;
}

@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.paper-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 0.75rem;
}

.paper-topics { display: flex; gap: 0.375rem; flex-wrap: wrap; }

.paper-topic-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.2rem 0.5rem;
    border-radius: var(--radius-pill);
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--pill-color, var(--text-muted));
    background: color-mix(in srgb, var(--pill-color, var(--accent)) 12%, transparent);
    white-space: nowrap;
}

.paper-topic-pill svg { width: 12px; height: 12px; }

.paper-number {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    background: var(--border-subtle);
    padding: 0.2rem 0.5rem;
    border-radius: var(--radius-sm);
    white-space: nowrap;
}

.paper-title {
    font-size: 1.05rem;
    font-weight: 600;
    line-height: 1.4;
    margin-bottom: 0.5rem;
}

.paper-title a { color: var(--text-primary); display: inline; }
.paper-title a:hover { color: var(--accent); }
.paper-title a svg { width: 14px; height: 14px; vertical-align: middle; opacity: 0.4; margin-left: 4px; }
.paper-title a:hover svg { opacity: 1; color: var(--accent); }

.paper-authors {
    font-size: 0.825rem;
    color: var(--text-secondary);
    margin-bottom: 0.25rem;
}

.expand-authors {
    background: none;
    border: none;
    color: var(--accent);
    font-family: var(--font-sans);
    font-size: 0.825rem;
    cursor: pointer;
    padding: 0;
}

.paper-authors-full.hidden { display: none; }

.paper-affiliations {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-bottom: 1rem;
}

.paper-tldr {
    margin-bottom: 1rem;
    padding: 1rem;
    background: var(--accent-glow);
    border-radius: var(--radius-sm);
}

.paper-tldr h4 {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--accent);
    margin-bottom: 0.5rem;
}

.paper-tldr p {
    font-size: 0.875rem;
    color: var(--text-primary);
    line-height: 1.6;
}

.paper-expandable { margin-bottom: 0.5rem; }

.expand-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0;
    border: none;
    background: none;
    color: var(--text-muted);
    font-family: var(--font-sans);
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    transition: color var(--transition);
}

.expand-btn:hover { color: var(--accent); }
.expand-btn svg { width: 14px; height: 14px; transition: transform var(--transition); }
.expand-btn.expanded svg { transform: rotate(180deg); }

.expandable-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}

.expandable-content.open { max-height: 1000px; }

.expandable-content p {
    padding: 0.75rem 0;
    font-size: 0.875rem;
    color: var(--text-secondary);
    line-height: 1.6;
}

.paper-footer {
    margin-top: 1rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--border-subtle);
}

.arxiv-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0.75rem;
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-sm);
    font-size: 0.8rem;
    color: var(--text-secondary);
    transition: all var(--transition);
}

.arxiv-btn:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-glow); }
.arxiv-btn svg { width: 14px; height: 14px; }
.arxiv-btn code { font-size: 0.8rem; }

/* ── Footer ── */
.footer {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
    border-top: 1px solid var(--border-subtle);
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    color: var(--text-muted);
}

.footer a { color: var(--text-muted); }
.footer a:hover { color: var(--accent); }

/* ── Utilities ── */
.hidden { display: none !important; }

/* ── Responsive ── */
@media (max-width: 767px) {
    .header-inner { padding: 0.5rem 1rem; }
    .logo span { font-size: 1rem; }
    .date-btn span { display: none; }
    .main { padding: 1.25rem 1rem; }
    .highlight-card { flex: 0 0 240px; }
    .footer { flex-direction: column; gap: 0.5rem; }
}
```

- [ ] **Step 2: Commit**

```bash
git add build/static/style.css
git commit -m "feat: add complete CSS with dark/light themes and responsive design"
```

---

### Task 10: Client-Side JavaScript

**Files:**
- Create: `build/static/app.js`

- [ ] **Step 1: Create app.js with all interactivity**

```javascript
/* build/static/app.js */
(function () {
    'use strict';

    // ── Theme Toggle ──
    const html = document.documentElement;
    const themeToggle = document.getElementById('theme-toggle');

    function setTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('arxiv-digest-theme', theme);
    }

    // Init theme from localStorage or system preference
    const saved = localStorage.getItem('arxiv-digest-theme');
    if (saved) {
        setTheme(saved);
    } else if (window.matchMedia('(prefers-color-scheme: light)').matches) {
        setTheme('light');
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const current = html.getAttribute('data-theme') || 'dark';
            setTheme(current === 'dark' ? 'light' : 'dark');
        });
    }

    // ── Date Dropdown ──
    const dateToggle = document.getElementById('date-toggle');
    const dateDropdown = document.getElementById('date-dropdown');

    if (dateToggle && dateDropdown) {
        dateToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            dateDropdown.classList.toggle('open');
        });

        document.addEventListener('click', function () {
            dateDropdown.classList.remove('open');
        });
    }

    // ── Search ──
    const searchToggle = document.getElementById('search-toggle');
    const searchBar = document.getElementById('search-bar');
    const searchInput = document.getElementById('search-input');
    const searchClose = document.getElementById('search-close');
    const paperCards = document.querySelectorAll('.paper-card');

    if (searchToggle && searchBar) {
        searchToggle.addEventListener('click', function () {
            searchBar.classList.toggle('open');
            if (searchBar.classList.contains('open')) {
                searchInput.focus();
            } else {
                searchInput.value = '';
                filterBySearch('');
            }
        });
    }

    if (searchClose) {
        searchClose.addEventListener('click', function () {
            searchBar.classList.remove('open');
            searchInput.value = '';
            filterBySearch('');
        });
    }

    let searchTimeout;
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function () {
                filterBySearch(searchInput.value);
            }, 150);
        });
    }

    function filterBySearch(query) {
        var q = query.toLowerCase().trim();
        paperCards.forEach(function (card) {
            if (!q) {
                card.setAttribute('data-search-hidden', 'false');
            } else {
                var title = (card.querySelector('.paper-title') || {}).textContent || '';
                var tldr = (card.querySelector('.paper-tldr') || {}).textContent || '';
                var match = title.toLowerCase().indexOf(q) !== -1 || tldr.toLowerCase().indexOf(q) !== -1;
                card.setAttribute('data-search-hidden', match ? 'false' : 'true');
            }
        });
        applyVisibility();
    }

    // ── Topic Filtering ──
    var topicPills = document.querySelectorAll('.topic-pill');
    var activeTopic = 'all';

    topicPills.forEach(function (pill) {
        pill.addEventListener('click', function () {
            topicPills.forEach(function (p) { p.classList.remove('active'); });
            pill.classList.add('active');
            activeTopic = pill.getAttribute('data-topic');
            applyVisibility();
            // Update URL hash
            if (activeTopic === 'all') {
                history.replaceState(null, '', window.location.pathname);
            } else {
                history.replaceState(null, '', '#' + encodeURIComponent(activeTopic));
            }
        });
    });

    // Restore filter from URL hash
    if (window.location.hash) {
        var hashTopic = decodeURIComponent(window.location.hash.slice(1));
        topicPills.forEach(function (pill) {
            if (pill.getAttribute('data-topic') === hashTopic) {
                pill.click();
            }
        });
    }

    function applyVisibility() {
        paperCards.forEach(function (card) {
            var topicMatch = activeTopic === 'all' || (card.getAttribute('data-topics') || '').indexOf(activeTopic) !== -1;
            var searchMatch = card.getAttribute('data-search-hidden') !== 'true';
            card.setAttribute('data-hidden', !(topicMatch && searchMatch));
        });
    }

    // ── Expand/Collapse ──
    document.querySelectorAll('.expand-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var targetId = btn.getAttribute('data-target');
            var target = document.getElementById(targetId);
            if (!target) return;
            var isOpen = target.classList.contains('open');
            target.classList.toggle('open');
            btn.classList.toggle('expanded');
            // Update button text
            var text = btn.textContent.trim();
            if (isOpen) {
                btn.innerHTML = btn.innerHTML.replace(/Hide/, 'Show');
            } else {
                btn.innerHTML = btn.innerHTML.replace(/Show/, 'Hide');
            }
        });
    });

    // ── Expand Authors ──
    document.querySelectorAll('.expand-authors').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var card = btn.closest('.paper-card');
            var short = card.querySelector('.paper-authors');
            var full = card.querySelector('.paper-authors-full');
            short.classList.add('hidden');
            full.classList.remove('hidden');
        });
    });

    // ── Scroll Animations ──
    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.05, rootMargin: '0px 0px -40px 0px' });

        paperCards.forEach(function (card) {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            observer.observe(card);
        });
    }
})();
```

- [ ] **Step 2: Commit**

```bash
git add build/static/app.js
git commit -m "feat: add client-side JS for filtering, search, theme, and animations"
```

---

### Task 11: Build Script

**Files:**
- Create: `build/build_site.py`

- [ ] **Step 1: Implement the main build orchestrator**

```python
#!/usr/bin/env python3
"""Build the arXiv Digest static site from .txt digest files."""
import glob
import json
import os
import re
import shutil

from jinja2 import Environment, FileSystemLoader

from build.parser import parse_digest
from build.clusterer import assign_topics, load_topics
from build.icons import svg_icon

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


def build():
    """Main build entry point."""
    # Setup output directory
    if os.path.exists(OUTPUT_DIR):
        # Preserve specs/plans subdirectories
        for item in os.listdir(OUTPUT_DIR):
            path = os.path.join(OUTPUT_DIR, item)
            if item == "superpowers":
                continue
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Copy static assets
    static_out = os.path.join(OUTPUT_DIR, "static")
    if os.path.exists(static_out):
        shutil.rmtree(static_out)
    shutil.copytree(STATIC_DIR, static_out)

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

    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False)

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
            highlights=highlights,
            overall_trend=digest["overall_trend"],
            topic_summary=topic_summary,
            papers=papers,
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
```

- [ ] **Step 2: Run the build and verify output**

Run: `cd /tmp/arxiv-digest && python -m build.build_site`
Expected output:
```
Built: 2026-04-09.html (13 papers)
Built: index.html -> 2026-04-09.html
```

- [ ] **Step 3: Verify generated files exist**

Run: `ls -la /tmp/arxiv-digest/docs/`
Expected: `index.html`, `2026-04-09.html`, and `static/` directory with `style.css` and `app.js`.

- [ ] **Step 4: Commit**

```bash
git add build/build_site.py
git commit -m "feat: implement build script for static site generation"
```

---

### Task 12: Integration Test

**Files:**
- Create: `tests/test_build.py`

- [ ] **Step 1: Write integration test that runs the full build**

```python
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
    assert "2026-04-09.html" in html
```

- [ ] **Step 2: Run all tests**

Run: `cd /tmp/arxiv-digest && python -m pytest tests/ -v`
Expected: All tests PASS (parser tests + clusterer tests + integration tests).

- [ ] **Step 3: Commit**

```bash
git add tests/test_build.py
git commit -m "test: add integration tests for full build pipeline"
```

---

### Task 13: GitHub Action for Auto-Deploy

**Files:**
- Create: `.github/workflows/build.yml`

- [ ] **Step 1: Create the GitHub Action workflow**

```yaml
# .github/workflows/build.yml
name: Build and Deploy Site

on:
  push:
    paths:
      - 'arxiv_digest/**'
      - 'build/**'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: python -m pytest tests/ -v

      - name: Build site
        run: python -m build.build_site

      - name: Commit and push
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "Rebuild site [skip ci]"
          file_pattern: "docs/*"
```

- [ ] **Step 2: Commit**

```bash
mkdir -p .github/workflows
git add .github/workflows/build.yml
git commit -m "ci: add GitHub Action to auto-rebuild site on digest push"
```

---

### Task 14: Run Full Build, Open in Browser, Visual QA

**Files:**
- No new files. This task verifies everything works end-to-end.

- [ ] **Step 1: Run full test suite**

Run: `cd /tmp/arxiv-digest && python -m pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 2: Run the build**

Run: `cd /tmp/arxiv-digest && python -m build.build_site`
Expected: Successful build output.

- [ ] **Step 3: Open in browser and verify**

Run: `cd /tmp/arxiv-digest/docs && python -m http.server 8765 &`

Open `http://localhost:8765` in browser. Verify:
- Dark theme renders correctly
- Header shows "arXiv Digest" with gradient text
- Date navigation shows "April 9, 2026"
- Top Highlights section shows 5 cards with topic colors
- Daily Trend banner shows with gradient top border
- Topic filter bar shows all topics with counts
- Clicking a topic pill filters paper cards
- Paper cards show in 2-column grid
- Each card has topic pills, title (clickable to arxiv), authors, TL;DR
- "Show take" and "Show abstract" expand/collapse
- Theme toggle switches to light mode
- Search filters cards by title/TL;DR
- Scroll animation works (cards fade in)
- Mobile responsive (resize window)

- [ ] **Step 4: Fix any visual issues found during QA**

Address any rendering bugs, spacing issues, or broken interactions.

- [ ] **Step 5: Final commit with all generated output**

```bash
git add docs/
git commit -m "feat: build initial site output"
```

---

### Task 15: Push and Enable GitHub Pages

**Files:**
- No new files.

- [ ] **Step 1: Push all commits to remote**

Run: `cd /tmp/arxiv-digest && git push origin main`

- [ ] **Step 2: Enable GitHub Pages**

Go to `https://github.com/adhirajghosh/arxiv-digest/settings/pages` and set:
- Source: "Deploy from a branch"
- Branch: `main`
- Folder: `/docs`

Or via CLI:
```bash
gh api repos/adhirajghosh/arxiv-digest/pages -X POST -f source.branch=main -f source.path=/docs
```

- [ ] **Step 3: Verify site is live**

Wait ~60 seconds, then visit: `https://adhirajghosh.github.io/arxiv-digest/`
Expected: The site loads with the April 9 digest.
