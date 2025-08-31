from pydantic import BaseModel
from .keyword import KeywordData

class KeywordResponse(BaseModel):
    total_keywords: int           # Raw count from APIs
    filtered_keywords: int        # After volume filter (>500)
    keywords: list[KeywordData]   # Final clean keyword list
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    message: str
