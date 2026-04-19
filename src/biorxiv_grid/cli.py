from __future__ import annotations

import argparse
import os
from pathlib import Path

from .config import load_config
from .pipeline import dump_results_json, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan latest bioRxiv preprints and filter/summarize.")
    parser.add_argument("--config", type=str, default=None, help="Path to JSON config file.")
    parser.add_argument("--out", type=str, default="outputs/latest_results.json", help="Output JSON file path.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = load_config(args.config)

    env_rel_key = os.getenv("BIORXIV_GRID_RELEVANCE_API_KEY")
    env_sum_key = os.getenv("BIORXIV_GRID_SUMMARY_API_KEY")
    if env_rel_key:
        config.llm_relevance.api_key = env_rel_key
    if env_sum_key:
        config.llm_summary.api_key = env_sum_key

    preprints = run_pipeline(config)

    out_path = Path(args.out)
    if out_path.parent != Path("."):
        out_path.parent.mkdir(parents=True, exist_ok=True)
    dump_results_json(out_path, preprints)

    print(f"Fetched + processed {len(preprints)} preprints")
    print(f"Saved to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
