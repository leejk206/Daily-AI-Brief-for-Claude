from pathlib import Path

from fetchers import validate_envelope
from fetchers.huggingface import parse

FIX_MODELS = Path(__file__).parent / "fixtures" / "huggingface_models.json"
FIX_PAPERS = Path(__file__).parent / "fixtures" / "huggingface_papers.json"


def test_parse_returns_valid_envelope():
    env = parse(FIX_MODELS.read_bytes(), FIX_PAPERS.read_bytes())
    validate_envelope(env)
    assert env["source"] == "huggingface"
    assert len(env["items"]) > 0


def test_items_tagged_by_type():
    env = parse(FIX_MODELS.read_bytes(), FIX_PAPERS.read_bytes())
    types = {item["signals"].get("type") for item in env["items"]}
    assert "model" in types
    if any(i["signals"].get("type") == "paper" for i in env["items"]):
        assert "paper" in types


def test_model_items_have_url():
    env = parse(FIX_MODELS.read_bytes(), FIX_PAPERS.read_bytes())
    models = [i for i in env["items"] if i["signals"].get("type") == "model"]
    assert len(models) > 0
    for m in models:
        assert m["url"].startswith("https://huggingface.co/")


def test_empty_inputs_return_empty_items():
    env = parse(b"[]", b"[]")
    validate_envelope(env)
    assert env["items"] == []
