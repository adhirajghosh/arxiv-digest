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
