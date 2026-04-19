from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Preprint:
    server: str
    doi: str
    title: str
    abstract: str
    authors: str
    date: str
    category: str
    version: str
    link: str
    score: float | None = None
    matched_keywords: list[str] = field(default_factory=list)
    relevance_reason: str | None = None
    summary: str | None = None

    @classmethod
    def from_api_record(cls, record: dict[str, Any], server: str = "biorxiv") -> "Preprint":
        doi = record.get("doi", "")
        return cls(
            server=server,
            doi=doi,
            title=record.get("title", ""),
            abstract=record.get("abstract", ""),
            authors=record.get("authors", ""),
            date=record.get("date", ""),
            category=record.get("category", ""),
            version=record.get("version", ""),
            link=f"https://www.biorxiv.org/content/{doi}v{record.get('version', '1')}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "server": self.server,
            "doi": self.doi,
            "title": self.title,
            "abstract": self.abstract,
            "authors": self.authors,
            "date": self.date,
            "category": self.category,
            "version": self.version,
            "link": self.link,
            "score": self.score,
            "matched_keywords": self.matched_keywords,
            "relevance_reason": self.relevance_reason,
            "summary": self.summary,
        }
