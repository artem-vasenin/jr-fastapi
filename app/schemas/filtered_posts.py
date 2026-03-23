from pydantic import BaseModel, HttpUrl
from datetime import datetime

class NewsItemOut(BaseModel):
    """Схема отфильтрованной новости"""
    title: str
    url: HttpUrl | None = None
    summary: str | None = None
    source: str
    published_at: datetime