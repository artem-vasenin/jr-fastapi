from pydantic import BaseModel, HttpUrl
from datetime import datetime

class PostsItemOut(BaseModel):
    """Схема сырой новости"""
    title: str
    url: str | None = None
    summary: str | None = None
    source: str
    published_at: datetime