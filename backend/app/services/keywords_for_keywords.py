import httpx
from typing import List, Dict, Any
from app.models.keyword import KeywordData, CompetitionLevel
from app.config import KEYWORDS_FOR_KEYWORDS_API_AUTH

class KeywordsForKeywordsService:
    
    # Factory pattern used for simplicity and not dependency injection
    def __init__(self):
        self.api_auth = KEYWORDS_FOR_KEYWORDS_API_AUTH
        self.base_url = "https://api.dataforseo.com/v3/keywords_data/google_ads/keywords_for_keywords/live"
        self.headers = {
            "Authorization": f"Basic {self.api_auth}",
            "Content-Type": "application/json"
        }
    
    async def get_keywords_from_seeds(self, keywords: List[str], location: str, 
                                      min_search_volume: int ) -> List[KeywordData]:

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                payload = [{
                    "location_name": location,
                    "language_name": "English", 
                    "keywords": keywords  # List of seed keywords
                }]
                
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    raise Exception(f"API error: {response.status_code} - {response.text}")
                
                keywords = []
                raw_data = response.json()
        
                # Navigate the response structure: tasks[0].result[]
                tasks = raw_data.get("tasks", [])
                if not tasks:
                    return keywords
                    
                result_list = tasks[0].get("result", [])
                
                for item in result_list:
                    try:
                        keyword_text = item.get("keyword", "").strip()
                        search_volume = int(item.get("search_volume", 0))
                        # Filter out low volume
                        if search_volume < min_search_volume:
                            continue

                        competition = item.get("competition", "MEDIUM").upper()
                        bid_low = float(item.get("low_top_of_page_bid", 0.0))
                        bid_high = float(item.get("high_top_of_page_bid", 0.0))
                        cpc = float(item.get("cpc", 0.0))

                        # Extract concept groups for LLM context
                        concept_groups = []
                        if "keyword_annotations" in item:
                            concepts = item["keyword_annotations"].get("concepts", [])
                            for concept in concepts:
                                group_name = concept.get("concept_group", {}).get("name")
                                if group_name:
                                    concept_groups.append(group_name)
                        
                        # Convert competition to correct format
                        if competition == "HIGH":
                            comp_level = CompetitionLevel.HIGH
                        elif competition == "LOW":
                            comp_level = CompetitionLevel.LOW
                        else:
                            comp_level = CompetitionLevel.MEDIUM
                        
                        # Only add valid keywords
                        if keyword_text:
                            keywords.append(KeywordData(
                                keyword=keyword_text,
                                search_volume=search_volume,
                                competition_level=comp_level,
                                bid_low=bid_low,
                                bid_high=bid_high,
                                cpc=cpc,
                                concept_groups=concept_groups
                            ))
                            
                    except (ValueError, KeyError, TypeError) as e:
                        # Skip invalid keyword data
                        continue


                return keywords
                
            except Exception as e:
                print(f"Error expanding keywords {keywords}: {str(e)}")
                return []
    
    def format_response(self, raw_data: Dict[str, Any], min_search_volume: int) -> List[KeywordData]:
    
        keywords = []
        
        # Navigate the response structure: tasks[0].result[]
        tasks = raw_data.get("tasks", [])
        if not tasks:
            return keywords
            
        result_list = tasks[0].get("result", [])
        
        for item in result_list:
            try:
                # Extract core keyword data
                keyword_text = item.get("keyword", "").strip()
                search_volume = int(item.get("search_volume", 0))
                
                # Filter out low volume
                if search_volume < min_search_volume:
                    continue

                competition = item.get("competition", "MEDIUM").upper()
                bid_low = float(item.get("low_top_of_page_bid", 0.0))
                bid_high = float(item.get("high_top_of_page_bid", 0.0))
                cpc = float(item.get("cpc", 0.0))

                # Extract concept groups for LLM context
                concept_groups = []
                if "keyword_annotations" in item:
                    concepts = item["keyword_annotations"].get("concepts", [])
                    for concept in concepts:
                        group_name = concept.get("concept_group", {}).get("name")
                        if group_name:
                            concept_groups.append(group_name)
                
                # Convert competition to our enum format
                if competition == "HIGH":
                    comp_level = CompetitionLevel.HIGH
                elif competition == "LOW":
                    comp_level = CompetitionLevel.LOW
                else:
                    comp_level = CompetitionLevel.MEDIUM
                
                # Only add valid keywords
                if keyword_text :
                    keywords.append(KeywordData(
                        keyword=keyword_text,
                        search_volume=search_volume,
                        competition_level=comp_level,
                        bid_low=bid_low,
                        bid_high=bid_high,
                        cpc=cpc,
                        concept_groups=concept_groups
                    ))
                    
            except (ValueError, KeyError, TypeError) as e:
                # Skip invalid keyword data
                continue
        
        return keywords
