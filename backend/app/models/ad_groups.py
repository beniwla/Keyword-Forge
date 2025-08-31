from pydantic import BaseModel
from typing import List, Optional

class SimpleKeyword(BaseModel):
    keyword: str
    search_volume: int
    competition_level: str  # "low", "medium", "high"
    cpc_low: float
    cpc_high: float
    suggested_match_types: List[str]  # ["exact", "phrase", "broad"]

class SimpleAdGroup(BaseModel):
    group_name: str
    group_type: str  # "brand", "category", "competitor", "location"
    keywords: List[SimpleKeyword]
    budget_allocation: float  # Dollar amount
    budget_percentage: float  # Percentage of total budget
    total_keywords: int
    avg_cpc_range: str  # "$1.50 - $3.00"

class SimplifiedDeliverable(BaseModel):
    ad_groups: List[SimpleAdGroup]
    total_budget: float
    total_keywords_used: int
    budget_summary: dict  # Simple breakdown by group type
    processing_time: float

class FinalKeywordResponse(BaseModel):
    # Basic extraction data
    total_keywords: int
    processing_time: float
    
    # LLM-generated ad groups
    deliverable: Optional[SimplifiedDeliverable] = None
