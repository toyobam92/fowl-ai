"""Shared Claude client, config, and JSON parsing for pipeline modules."""

import json
import os
import sys
from pathlib import Path

import yaml
from anthropic import Anthropic

ROOT = Path(__file__).resolve().parent.parent
CONFIG = yaml.safe_load((ROOT / "config.yaml").read_text())
MODEL = CONFIG.get("model", "claude-sonnet-4-6")


def client() -> Anthropic:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set")
    return Anthropic()


def call(client: Anthropic, system: str, user: str, max_tokens: int = 4000) -> str:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def parse_json(raw: str) -> dict | None:
    """Parse a model JSON reply, tolerating markdown fences. None if unparseable."""
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None
