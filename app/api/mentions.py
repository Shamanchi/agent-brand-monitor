"""Эндпоинты мониторинга бренда."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.services.store import Alert, Mention, MentionStore, SentimentSummary, get_store

router = APIRouter()


class MentionRequest(BaseModel):
    source: str = Field(default="unknown", max_length=64)
    text: str = Field(min_length=1, max_length=5000)


def get_book() -> MentionStore:
    return get_store()


@router.post("/mentions", response_model=Mention)
async def add_mention(request: MentionRequest, book: MentionStore = Depends(get_book)) -> Mention:
    try:
        return book.add(request.source, request.text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/mentions", response_model=list[Mention])
async def mentions(book: MentionStore = Depends(get_book)) -> list[Mention]:
    return book.all_mentions()


@router.get("/sentiment", response_model=SentimentSummary)
async def sentiment(book: MentionStore = Depends(get_book)) -> SentimentSummary:
    return book.summary()


@router.get("/alerts", response_model=list[Alert])
async def alerts(
    book: MentionStore = Depends(get_book),
    settings: Settings = Depends(get_settings),
) -> list[Alert]:
    return book.alerts(window=settings.negative_window, threshold=settings.negative_threshold)


@router.get("/digest")
async def digest(book: MentionStore = Depends(get_book)) -> dict:
    return {"digest_md": book.digest()}
