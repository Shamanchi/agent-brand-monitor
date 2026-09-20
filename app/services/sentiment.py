"""Словарная тональность упоминаний (EN+RU), без сети."""

from __future__ import annotations

import re

POSITIVE = {
    "love", "great", "excellent", "awesome", "amazing", "good", "best",
    "fantastic", "perfect", "recommend", "thanks", "thank", "like",
    "отлично", "отличный", "супер", "класс", "хорошо", "хороший", "лучший",
    "спасибо", "рекомендую", "нравится", "прекрасно", "замечательно", "люблю",
}

NEGATIVE = {
    "hate", "terrible", "awful", "horrible", "bad", "worst", "broken",
    "bug", "crash", "slow", "disappointed", "angry", "refund", "scam",
    "ужас", "ужасный", "плохо", "плохой", "худший", "ненавижу", "разочарован",
    "возврат", "мошенники", "обман", "тормозит", "сломан",
}

_WORD_RE = re.compile(r"[a-zA-Zа-яА-ЯёЁ]+")


def score_text(text: str) -> float:
    """Оценка -1..1: (pos-neg)/(pos+neg), 0 при отсутствии маркеров."""
    words = _WORD_RE.findall(text.lower())
    pos = sum(1 for w in words if w in POSITIVE)
    neg = sum(1 for w in words if w in NEGATIVE)
    if pos + neg == 0:
        return 0.0
    return round((pos - neg) / (pos + neg), 2)


def label(score: float) -> str:
    if score > 0.2:
        return "positive"
    if score < -0.2:
        return "negative"
    return "neutral"
