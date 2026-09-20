"""Unit-тесты тональности и хранилища: без сети."""

import pytest

from app.services.sentiment import label, score_text
from app.services.store import MentionStore


def test_score_polarity() -> None:
    assert score_text("Love it, great support!") > 0
    assert score_text("Terrible crash, awful bug") < 0
    assert score_text("The meeting is at noon") == 0.0
    assert score_text("Отличный сервис, спасибо!") > 0
    assert score_text("Ужасный обман, возврат денег") < 0


def test_labels() -> None:
    assert label(0.8) == "positive"
    assert label(-0.8) == "negative"
    assert label(0.0) == "neutral"


def test_store_summary() -> None:
    store = MentionStore()
    store.add("x", "Love it, great!")
    store.add("x", "The meeting is at noon")
    store.add("x", "Terrible awful crash")
    store.add("x", "The server runs daily")
    summary = store.summary()
    assert summary.total == 4
    assert (summary.positive, summary.neutral, summary.negative) == (1, 2, 1)
    assert summary.index == 0.0


def test_alerts_spike() -> None:
    store = MentionStore()
    for _ in range(3):
        store.add("x", "Terrible awful crash")
    alerts = store.alerts(window=10, threshold=0.5)
    assert len(alerts) == 1
    assert alerts[0].kind == "negative_spike"


def test_no_alerts_when_calm() -> None:
    store = MentionStore()
    store.add("x", "Love it, great!")
    assert store.alerts(window=10, threshold=0.5) == []
    assert MentionStore().alerts() == []


def test_rejects_empty() -> None:
    with pytest.raises(ValueError):
        MentionStore().add("x", "   ")
