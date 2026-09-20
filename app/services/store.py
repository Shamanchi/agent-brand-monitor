"""Хранилище упоминаний и агрегаты (in-memory, офлайн)."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel

from app.services.sentiment import label, score_text


class Mention(BaseModel):
    id: str
    source: str
    text: str
    score: float
    label: str
    created_at: str


class SentimentSummary(BaseModel):
    total: int
    index: float
    positive: int
    neutral: int
    negative: int


class Alert(BaseModel):
    kind: str
    detail: str


class MentionStore:
    """Журнал упоминаний с тональностью."""

    def __init__(self) -> None:
        self._mentions: list[Mention] = []

    def add(self, source: str, text: str) -> Mention:
        if not text or not text.strip():
            raise ValueError("text must not be empty")
        score = score_text(text)
        mention = Mention(
            id=str(uuid4()),
            source=source.strip() or "unknown",
            text=text.strip(),
            score=score,
            label=label(score),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._mentions.append(mention)
        return mention

    def all_mentions(self) -> list[Mention]:
        return list(self._mentions)

    def summary(self) -> SentimentSummary:
        total = len(self._mentions)
        if total == 0:
            return SentimentSummary(total=0, index=0.0, positive=0, neutral=0, negative=0)
        positive = sum(1 for m in self._mentions if m.label == "positive")
        negative = sum(1 for m in self._mentions if m.label == "negative")
        neutral = total - positive - negative
        index = round(sum(m.score for m in self._mentions) / total, 2)
        return SentimentSummary(
            total=total, index=index, positive=positive, neutral=neutral, negative=negative
        )

    def alerts(self, window: int = 10, threshold: float = 0.5) -> list[Alert]:
        """Алерт, если доля негатива в последних `window` упоминаниях >= threshold."""
        recent = self._mentions[-window:] if window > 0 else []
        if not recent:
            return []
        negative = sum(1 for m in recent if m.label == "negative")
        share = negative / len(recent)
        if share >= threshold:
            return [
                Alert(
                    kind="negative_spike",
                    detail=f"{negative}/{len(recent)} negative in last {len(recent)} ({share:.0%})",
                )
            ]
        return []

    def digest(self) -> str:
        summary = self.summary()
        lines = [
            "# Brand digest",
            "",
            f"- Mentions: {summary.total}, index {summary.index:+}",
            f"- Positive {summary.positive}, neutral {summary.neutral}, negative {summary.negative}",
        ]
        negatives = [m for m in self._mentions if m.label == "negative"][-5:]
        if negatives:
            lines.append("- Recent negatives:")
            lines.extend(f"  - [{m.source}] {m.text[:80]}" for m in negatives)
        else:
            lines.append("- No negative mentions.")
        return "\n".join(lines) + "\n"

    def clear(self) -> None:
        self._mentions.clear()


_store: MentionStore | None = None


def get_store() -> MentionStore:
    global _store
    if _store is None:
        _store = MentionStore()
    return _store
