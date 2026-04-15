# arXiv Digest Website Design Spec

**Date**: 2026-04-15
**Status**: Approved
**Hosting**: GitHub Pages on existing `adhirajghosh/arxiv-digest` repo, served from `docs/` folder

## Overview

Transform the plain-text arXiv digest repository into an aesthetic, interactive static website with topic clustering, clickable paper links, and automatic rebuilds on new digest pushes.

## Architecture

```
arxiv-digest/
├── arxiv_digest/              # Existing digest data (unchanged)
│   └── april_26/
│       └── 2026-04-09.txt
├── build/
│   ├── build_site.py          # Main build script
│   ├── parser.py              # Parses .txt digests into structured data
│   ├── clusterer.py           # Groups papers into topic clusters
│   ├── templates/
│   │   └── index.html         # Jinja2 template for the site
│   │   └── digest.html        # Jinja2 template for individual digest pages
│   └── static/
│       ├── style.css          # All styles
│       └── app.js             # Client-side interactivity
├── docs/                      # GitHub Pages output (generated, committed)
│   ├── index.html             # Redirects to latest digest
│   ├── 2026-04-09.html        # Per-date pages
│   └── static/
│       ├── style.css
│       └── app.js
├── .github/
│   └── workflows/
│       └── build.yml          # On push to arxiv_digest/ → rebuild → commit
└── requirements.txt           # jinja2, pyyaml
```

**Data flow**: `.txt` files -> `parser.py` extracts structured paper data -> `clusterer.py` assigns topic clusters -> `build_site.py` renders Jinja2 templates -> static HTML in `docs/` deployed by GitHub Pages.

## Parser (`build/parser.py`)

Reads each `.txt` file and extracts structured data using regex against the consistent formatting:

```python
# Output structure per digest
{
  "date": "2026-04-09",
  "date_display": "April 9, 2026",
  "highlights": [
    {"title": "VLMs Need Words", "summary": "reveals that VLMs systematically fail..."},
    ...
  ],
  "papers": [
    {
      "number": 1,
      "title": "VLMs Need Words: Vision Language Models...",
      "authors": "Haz Sameen Shahgir, Xiaofu Chen, ...",
      "affiliations": "UC Riverside; MBZUAI",
      "arxiv_url": "https://arxiv.org/abs/2604.02486",
      "arxiv_id": "2604.02486",
      "abstract": "...",
      "tldr": "...",
      "take": "...",
      "topics": ["VLM Architecture", "Training"]  # Assigned by clusterer
    },
    ...
  ],
  "overall_trend": "Today's submissions reveal a maturing field..."
}
```

Parsing approach:
- Split on `---` separators to isolate paper blocks
- Extract title from `### N. Title` pattern
- Extract fields from `**FieldName:** value` pattern
- Extract link from `**Link:** url` pattern
- Top Highlights from bullet points under `## Top Highlights Today`
- Overall Trend from text under `## Overall Trend Today`

## Topic Clustering (`build/clusterer.py`)

Keyword-based topic assignment with a configurable taxonomy.

### Topic Taxonomy (~15 topics)

Defined in `build/topics.yaml`:

```yaml
topics:
  - name: "VLM Architecture"
    icon: "brain-circuit"      # Lucide-style SVG icon name
    color: "#8b5cf6"           # Violet
    keywords: ["VLM", "vision-language", "multimodal model", "unified model", "architecture", "latent space"]

  - name: "Hallucination"
    icon: "eye-off"
    color: "#f59e0b"           # Amber
    keywords: ["hallucination", "hallucinate", "faithfulness", "grounding"]

  - name: "Video Understanding"
    icon: "film"
    color: "#10b981"           # Emerald
    keywords: ["video", "temporal", "streaming", "VideoLLM", "video understanding"]

  - name: "Benchmarks & Evaluation"
    icon: "bar-chart-3"
    color: "#06b6d4"           # Cyan
    keywords: ["benchmark", "evaluation", "eval", "dataset", "annotation"]

  - name: "3D & Spatial"
    icon: "box"
    color: "#ec4899"           # Pink
    keywords: ["3D", "spatial", "multi-view", "depth", "geometry", "consistency"]

  - name: "Training & Distillation"
    icon: "zap"
    color: "#f97316"           # Orange
    keywords: ["distillation", "fine-tuning", "SFT", "RLHF", "training", "pretraining"]

  - name: "Generation"
    icon: "palette"
    color: "#a855f7"           # Purple
    keywords: ["generation", "generative", "diffusion", "image generation", "video generation"]

  - name: "Streaming & Real-time"
    icon: "radio"
    color: "#14b8a6"           # Teal
    keywords: ["streaming", "real-time", "always-on", "live", "deployment"]

  - name: "Multilingual"
    icon: "globe"
    color: "#6366f1"           # Indigo
    keywords: ["Japanese", "multilingual", "non-English", "cross-lingual"]

  - name: "Reasoning"
    icon: "git-branch"
    color: "#eab308"           # Yellow
    keywords: ["reasoning", "chain-of-thought", "planning", "logic"]

  - name: "Robustness"
    icon: "shield"
    color: "#ef4444"           # Red
    keywords: ["degraded", "robust", "noisy", "corruption", "adversarial"]

  - name: "Attention & Interpretability"
    icon: "scan-eye"
    color: "#84cc16"           # Lime
    keywords: ["attention", "interpretability", "explainability", "evidence"]

  - name: "Infrastructure & Tooling"
    icon: "wrench"
    color: "#78716c"           # Stone
    keywords: ["framework", "infrastructure", "tooling", "library", "open-source"]
```

### Assignment Algorithm

```
For each paper:
  score each topic = count of keyword matches in (title + tldr), case-insensitive
  assign top 1-2 topics (those with score > 0, max 2)
  if no topic matches, assign "General"
```

## Visual Design

### Color Palette

**Dark mode (default)**:
- `--bg-primary`: `#0a0a0f` (near-black with blue tint)
- `--bg-card`: `#13131a`
- `--bg-card-hover`: `#1a1a24`
- `--border-subtle`: `rgba(255,255,255,0.06)`
- `--text-primary`: `#e4e4e7`
- `--text-secondary`: `#a1a1aa`
- `--text-muted`: `#71717a`
- `--accent`: `#8b5cf6` (violet)
- `--accent-glow`: `rgba(139,92,246,0.15)`

**Light mode**:
- `--bg-primary`: `#fafafa`
- `--bg-card`: `#ffffff`
- `--bg-card-hover`: `#f4f4f5`
- `--border-subtle`: `rgba(0,0,0,0.08)`
- `--text-primary`: `#18181b`
- `--text-secondary`: `#52525b`
- `--text-muted`: `#a1a1aa`
- `--accent`: `#7c3aed`

### Typography

- Font stack: `Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- Headings: 700 weight
- Body: 400 weight, 16px base, 1.6 line height
- Monospace (arxiv IDs): `'JetBrains Mono', 'Fira Code', monospace`

### Icons

Inline SVG icons embedded in the template. Each topic gets a unique icon from the Lucide icon set (open-source, MIT licensed). Icons are defined as SVG path data in `topics.yaml` or inlined in the template.

Additional UI icons:
- External link (for arxiv buttons)
- Sun/Moon (theme toggle)
- ChevronLeft/ChevronRight (date navigation)
- Calendar (date picker)
- Search (search bar)
- ChevronDown (expand/collapse)

## Page Layout

### Structure (top to bottom)

1. **Header Bar**
   - Left: Site logo/title "arXiv Digest" with subtle gradient text
   - Center: Date navigation (< prev | "April 9, 2026" dropdown | next >)
   - Right: Search icon, theme toggle (sun/moon)
   - Sticky on scroll with backdrop blur

2. **Hero Section — Top Highlights**
   - Horizontal scrollable row of 5 accent-colored cards
   - Each card: topic icon, title (clickable to arxiv), one-line TL;DR excerpt, topic pill
   - Cards have subtle gradient left-border matching topic color
   - Section title: "Top Highlights" with sparkle icon

3. **Daily Trend Banner**
   - Full-width styled callout with gradient border
   - "Today's Trend" label with trend icon
   - Contains the Overall Trend text from the digest
   - Collapsible on mobile

4. **Topic Filter Bar**
   - Horizontal scrollable row of topic pills
   - Each pill: icon + name + paper count badge
   - "All" pill selected by default
   - Active pill gets filled background in topic color
   - Inactive pills are outlined/ghost style
   - Sticky below header on scroll

5. **Paper Cards Grid**
   - 2-column CSS Grid on desktop, 1-column on mobile
   - Breakpoint at 768px
   - Each card:
     - Top row: topic icon + topic pill(s) | paper number badge
     - Title (large, bold, clickable link to arxiv)
     - Author line (truncated to ~3 authors + "et al.", full list on expand)
     - Affiliations (smaller, muted text)
     - TL;DR section (always visible, the primary read content)
     - "Take" section (collapsed by default, "Show take" toggle)
     - "Abstract" section (collapsed by default, "Show abstract" toggle)
     - Bottom row: arxiv link button with external-link icon, arxiv ID in monospace
   - Cards have left-border accent color matching primary topic
   - Subtle hover effect (lift + shadow)

6. **Footer**
   - "Built with arXiv Digest" credit
   - GitHub repo link
   - "Papers sourced from arXiv.org"

### Responsive Breakpoints
- `>= 1200px`: 2-column grid, full hero row
- `768px - 1199px`: 2-column grid, scrollable hero
- `< 768px`: 1-column, stacked hero cards, collapsible trend

## Client-Side Interactivity (`build/static/app.js`)

Vanilla JS, no framework. Features:

1. **Topic filtering**: Click pill -> toggle `data-hidden` attribute on non-matching cards, CSS transition (fade + collapse). Filter state reflected in URL hash for shareability.

2. **Expand/collapse**: Toggle sections (take, abstract, authors) with slide animation using `max-height` transition. State not persisted.

3. **Date navigation**: Links to other date HTML files (`/2026-04-09.html`, etc.). Prev/next arrows, dropdown shows available dates.

4. **Theme toggle**: Toggles `data-theme="light"` on `<html>`. Saved to `localStorage`. Respects `prefers-color-scheme` on first visit.

5. **Scroll animations**: Cards fade in on viewport entry using `IntersectionObserver`. Subtle `translateY(20px)` to `translateY(0)` animation.

6. **Search**: Text input filters cards by matching title and TL;DR content. Debounced input, instant results.

## Build & Deploy Pipeline

### GitHub Action (`.github/workflows/build.yml`)

```yaml
name: Build and Deploy Site
on:
  push:
    paths:
      - 'arxiv_digest/**'
      - 'build/**'
  workflow_dispatch:  # Manual trigger

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
      - run: pip install -r requirements.txt
      - run: python build/build_site.py
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "Rebuild site"
          file_pattern: "docs/*"
```

### Build Script (`build/build_site.py`)

1. Glob all `.txt` files under `arxiv_digest/`
2. Parse each into structured data via `parser.py`
3. Sort digests by date (newest first)
4. Run topic clustering via `clusterer.py`
5. For each digest, render `digest.html` template -> `docs/YYYY-MM-DD.html`
6. Render `index.html` template (redirects to latest date) -> `docs/index.html`
7. Copy static assets to `docs/static/`

### Multi-Date Strategy

- One HTML file per date: `docs/2026-04-09.html`
- `docs/index.html` contains a meta-redirect to the latest date's page
- Each page includes a date navigation dropdown listing all available dates
- Available dates are embedded as a JSON array in each page

## Scope Exclusions

- No backend server
- No database
- No user accounts
- No comments or social features
- No RSS feed
- No email notifications
- No LLM calls during build
- No external API calls during build
- No analytics or tracking
