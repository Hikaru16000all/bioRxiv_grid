from __future__ import annotations

import textwrap

from .llm import LLMClient
from .models import Preprint


def keyword_filter(preprints: list[Preprint], keywords: list[str]) -> list[Preprint]:
    if not keywords:
        return preprints

    normalized = [k.strip().lower() for k in keywords if k.strip()]
    results: list[Preprint] = []

    for p in preprints:
        haystack = f"{p.title}\n{p.abstract}".lower()
        matched = [k for k in normalized if k in haystack]
        if matched:
            p.matched_keywords = matched
            p.score = float(len(matched)) / float(len(normalized))
            results.append(p)
    return results


def llm_relevance_filter(
    preprints: list[Preprint],
    description: str,
    llm_client: LLMClient,
    threshold: float = 0.5,
) -> list[Preprint]:
    if not description.strip():
        return preprints

    selected: list[Preprint] = []
    system_prompt = (
        "你是科研文献筛选助手。输出JSON: "
        '{"score":0~1浮点数,"reason":"一句话理由"}。不要输出额外字段。'
    )

    for p in preprints:
        user_prompt = textwrap.dedent(
            f"""
            用户的目标描述：{description}

            论文标题：{p.title}
            论文摘要：{p.abstract}

            请判断该论文是否匹配目标描述。
            """
        ).strip()

        result = llm_client.chat_json(system_prompt=system_prompt, user_prompt=user_prompt)
        score = float(result.get("score", 0.0))
        p.score = score
        p.relevance_reason = str(result.get("reason", ""))
        if score >= threshold:
            selected.append(p)

    return selected
