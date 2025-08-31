from pydantic import BaseModel, HttpUrl
from typing import Optional

class KeywordResearchRequest(BaseModel):
    # For minimal site content (Scenario 1)
    seed_keywords: Optional[list[str]] = None
    
    # Required inputs
    brand_website: HttpUrl
    competitor_website: HttpUrl
    location: str
    shopping_ads_budget: float
    search_ads_budget: float
    pmax_ads_budget: float
    min_search_volume: int
    
