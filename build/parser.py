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
        "topics": [],
    }


def _extract_overall_trend(text: str) -> str:
    """Extract the overall trend section text."""
    return _extract_section(text, "Overall Trend Today").strip()


def _extract_section(text: str, heading: str) -> str:
    """Extract text between a ## heading and the next ## heading (or end)."""
    pattern = rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""
