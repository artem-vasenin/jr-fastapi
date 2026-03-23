from pydantic import BaseModel
from datetime import datetime

class DupHistoryOut(BaseModel):
    """Схема опубликованной новости"""
    hash: str
    title: str
    summary: str
    source: str
    published_at: datetime
