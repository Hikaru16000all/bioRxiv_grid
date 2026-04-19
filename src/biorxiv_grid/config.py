from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class LLMConfig:
    enabled: bool = False
    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4.1-mini"
    timeout_sec: int = 40


@dataclass
class AppConfig:
    days_back: int = 1
    max_records: int = 200
    keywords: list[str] | None = None
    description: str | None = None
    relevance_threshold: float = 0.5
    llm_relevance: LLMConfig = field(default_factory=LLMConfig)
    llm_summary: LLMConfig = field(default_factory=LLMConfig)


def _merge_dict(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            merged[key] = _merge_dict(base[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | Path | None) -> AppConfig:
    if not path:
        return AppConfig()

    raw = json.loads(Path(path).read_text(encoding="utf-8"))

    defaults = {
        "days_back": 1,
        "max_records": 200,
        "keywords": [],
        "description": None,
        "relevance_threshold": 0.5,
        "llm_relevance": {
            "enabled": False,
            "api_key": None,
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4.1-mini",
            "timeout_sec": 40,
        },
        "llm_summary": {
            "enabled": False,
            "api_key": None,
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4.1-mini",
            "timeout_sec": 40,
        },
    }

    merged = _merge_dict(defaults, raw)

    return AppConfig(
        days_back=int(merged["days_back"]),
        max_records=int(merged["max_records"]),
        keywords=[str(x) for x in merged.get("keywords", [])],
        description=merged.get("description"),
        relevance_threshold=float(merged["relevance_threshold"]),
        llm_relevance=LLMConfig(**merged["llm_relevance"]),
        llm_summary=LLMConfig(**merged["llm_summary"]),
    )
