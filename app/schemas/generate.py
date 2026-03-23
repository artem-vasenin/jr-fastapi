from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    """Схема запроса на генерацию"""
    title: str = Field(..., min_length=5, max_length=300)
    summary: str = Field(..., min_length=10, max_length=2000)

class GenerateResponse(BaseModel):
    """Схема ответа со сгенерированной новостью"""
    original_title: str
    new_title: str
    generated_post: str

class GeneratedPostOut(GenerateResponse):
    """Схема сгенерированной и сохраненной новости"""
    key: str = Field(..., description="Redis-ключ записи")
    hash: str = Field(..., description="MD5 хеш оригинала")