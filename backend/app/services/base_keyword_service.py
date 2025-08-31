import asyncio
from typing import List
from app.models.keyword import KeywordData
from app.models.requests import KeywordResearchRequest
from app.services.keywords_for_site import KeywordsForSiteService
from app.services.keywords_for_keywords import KeywordsForKeywordsService

class BaseKeywordService:
    
    # Orchestrating all APIs
    # Factory pattern used for simplicity and not dependency injection
    def __init__(self):
        self.keywords_for_site_service = KeywordsForSiteService()
        self.keywords_for_keywords_service = KeywordsForKeywordsService()
    
    async def extract_all_keywords(self, request: KeywordResearchRequest) -> List[KeywordData]:
        """
        Extract keywords from all sources concurrently so httpx used instead of normal requests:
        - Scenario 1: seed_keywords + brand + competitor (3 API calls)
        - Scenario 2: brand + competitor only (2 API calls)
        """
        tasks = []
        location = request.location  # Use first location from list
        min_search_volume = request.min_search_volume
        
        # Task 1: Seed keywords (if provided) - KeywordsForKeywords API
        if request.seed_keywords and len(request.seed_keywords) > 0:
            tasks.append(
                self.keywords_for_keywords_service.get_keywords_from_seeds(
                    keywords=request.seed_keywords,
                    location=location,
                    min_search_volume=min_search_volume
                )
            )
        
        # Task 2: Brand website - KeywordsForSite API  
        tasks.append(
            self.keywords_for_site_service.get_keywords_from_site(
                website_url=str(request.brand_website),
                location=location,
                min_search_volume=min_search_volume
            )
        )
        
        # Task 3: Competitor website - KeywordsForSite API
        tasks.append(
            self.keywords_for_site_service.get_keywords_from_site(
                website_url=str(request.competitor_website),
                location=location,
                min_search_volume=min_search_volume
            )
        )
        
        # Execute all tasks concurrently using asyncio.gather
        print(f"Starting {len(tasks)} API calls concurrently...")
        results = await asyncio.gather(*tasks, return_exceptions=True) 
        
        # *tasks-> unpacks the list's elements
        # with return_exceptions = true, whole thing doesn't crash as we append the exception(e) in results

        # Combine all results and handle exceptions
        all_keywords = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Task {i+1} failed: {str(result)}")
                continue
            
            if isinstance(result, list):
                all_keywords.extend(result)
                print(f"Task {i+1} returned {len(result)} keywords")
        
        # Remove duplicates based on keyword text
        unique_keywords = self._remove_duplicates(all_keywords)
        
        print(f"Total unique keywords extracted: {len(unique_keywords)}")
        return unique_keywords
    

    def _remove_duplicates(self, keywords: List[KeywordData]) -> List[KeywordData]:
        
        seen_keywords = set()
        unique_keywords = []
        
        for keyword in keywords:
            if keyword.keyword.lower() not in seen_keywords:
                seen_keywords.add(keyword.keyword.lower())
                unique_keywords.append(keyword)
        
        return unique_keywords
