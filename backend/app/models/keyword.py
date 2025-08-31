from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class CompetitionLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class KeywordData(BaseModel):
    keyword: str
    search_volume: int
    competition_level: CompetitionLevel
    bid_low: float
    bid_high: float
    cpc:float
    concept_groups: Optional[List[str]] = []  # NEW: For deliverable 1

class KeywordList(BaseModel):
    keywords: list[KeywordData]
    total_count: int
