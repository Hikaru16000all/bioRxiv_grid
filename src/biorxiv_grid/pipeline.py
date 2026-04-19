from __future__ import annotations

import json
from pathlib import Path

from .biorxiv_client import BioRxivClient
from .config import AppConfig
from .filter_engine import keyword_filter, llm_relevance_filter
from .llm import LLMClient
from .models import Preprint
from .summarizer import summarize_preprints


def run_pipeline(config: AppConfig) -> list[Preprint]:
    client = BioRxivClient()
    preprints = client.fetch_latest(
        days_back=config.days_back,
        max_records=config.max_records,
        end_lag_days=config.end_lag_days,
    )

    if config.keywords:
        preprints = keyword_filter(preprints, config.keywords)

    if config.description and config.llm_relevance.enabled:
        if not config.llm_relevance.api_key:
            raise ValueError("llm_relevance.enabled=true 时必须提供 api_key")
        relevance_client = LLMClient(
            api_key=config.llm_relevance.api_key,
            base_url=config.llm_relevance.base_url,
            model=config.llm_relevance.model,
            timeout_sec=config.llm_relevance.timeout_sec,
        )
        preprints = llm_relevance_filter(
            preprints,
            description=config.description,
            llm_client=relevance_client,
            threshold=config.relevance_threshold,
        )

    if config.llm_summary.enabled:
        if not config.llm_summary.api_key:
            raise ValueError("llm_summary.enabled=true 时必须提供 api_key")
        summary_client = LLMClient(
            api_key=config.llm_summary.api_key,
            base_url=config.llm_summary.base_url,
            model=config.llm_summary.model,
            timeout_sec=config.llm_summary.timeout_sec,
        )
        preprints = summarize_preprints(preprints, summary_client)

    return preprints


def dump_results_json(path: str | Path, preprints: list[Preprint]) -> None:
    data = [p.to_dict() for p in preprints]
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
