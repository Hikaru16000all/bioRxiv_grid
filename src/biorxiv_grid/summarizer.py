from __future__ import annotations

import textwrap

from .llm import LLMClient
from .models import Preprint


def summarize_preprints(preprints: list[Preprint], llm_client: LLMClient) -> list[Preprint]:
    system_prompt = (
        "你是学术论文摘要助手。输出JSON: "
        '{"summary":"3-5句中文总结，包含研究问题、方法、结论"}'
    )

    for p in preprints:
        user_prompt = textwrap.dedent(
            f"""
            标题：{p.title}
            摘要：{p.abstract}
            """
        ).strip()
        result = llm_client.chat_json(system_prompt=system_prompt, user_prompt=user_prompt)
        p.summary = str(result.get("summary", "")).strip()

    return preprints
