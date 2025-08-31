import openai
import json
import time
import logging
from typing import List
from app.models.keyword import KeywordData, CompetitionLevel
from app.models.requests import KeywordResearchRequest
from app.models.ad_groups import SimplifiedDeliverable, SimpleAdGroup, SimpleKeyword
from app.config import OPENAI_API_KEY

# logging setup 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    async def create_ad_groups(self, keywords: List[KeywordData], request: KeywordResearchRequest) -> SimplifiedDeliverable:
        """LLM call to group keywords into ad groups"""
        start_time = time.time()
        
        try:
            logger.info(f"Starting LLM with {len(keywords)} keywords")

            #Create top_n priority keywords
            priority_keywords = self._create_priority_keywords(keywords, 20)
            logger.info("Priority keywords extracted created successfully")

            # Build simple prompt
            # Take first top_n keywords as 8000 token limit on openai model
            prompt = self._create_prompt(priority_keywords, request.search_ads_budget)
            logger.info("Prompt created successfully")
            
            # Call OpenAI
            response = await self._call_llm(prompt)
            logger.info("OpenAI call successful")
            
            # Parse response
            result = self._parse_json(response, request.search_ads_budget, len(keywords))
            result.processing_time = time.time() - start_time

            logger.info(f"LLM service completed successfully in {result.processing_time:.1f}s")
            
            return result
        
        except Exception as e:
            logger.error(f"LLM failed: {str(e)}")
            return self._create_fallback(request.search_ads_budget, len(keywords))
    
    def _create_priority_keywords(self, keywords: List[KeywordData], top_n: int) -> List[KeywordData]:

        try:

            logger.info(f"Starting priority selection: {len(keywords)} keywords -> top {top_n}")

            min_volume = min(kw.search_volume for kw in keywords if kw.search_volume is not None)
            max_volume = max(kw.search_volume for kw in keywords if kw.search_volume is not None)
            cpc_min = min(kw.cpc for kw in keywords if kw.cpc is not None)
            cpc_max = max(kw.cpc for kw in keywords if kw.cpc is not None)

            logger.info(f"Volume range: {min_volume}-{max_volume}, CPC range: {cpc_min:.2f}-{cpc_max:.2f}")

            weights = [0.4, 0.3, 0.3] # weights for search_vol, cpc, competition

            final_scores = []
            for kw in keywords:

                if max_volume == min_volume:
                    norm_volume = 0.5  
                else:
                    norm_volume = (kw.search_volume - min_volume) / (max_volume - min_volume)

                if cpc_max == cpc_min:
                    norm_cpc = 0.5
                else:
                    norm_cpc = 1 - ((kw.cpc - cpc_min)/(cpc_max - cpc_min))

                if kw.competition_level == CompetitionLevel.HIGH : norm_comp = 0
                elif kw.competition_level == CompetitionLevel.LOW : norm_comp = 1
                else: norm_comp = 0.5

                weighted_score = weights[0]*norm_volume + weights[1]*norm_cpc + weights[2]*norm_comp
                final_scores.append((weighted_score, kw))

            logger.info("Scoring completed, sorting by priority")

            final_scores.sort(key=lambda x: x[0], reverse=True)

            top_keywords = [priority_scores[1] for priority_scores in final_scores[:top_n]] # return first top_n priority keywords
            
            logger.info(f"Priority selection complete: selected {len(top_keywords)} keywords")
            
            # Log top 3 keywords for verification
            for i, kw in enumerate(top_keywords[:3]):
                score = final_scores[i][0]
                logger.info(f"Top {i+1}: '{kw.keyword}' (score: {score:.3f})")
            
            return top_keywords
        
        except ValueError as e:
            logger.error(f"Priority selection failed - no valid keywords: {str(e)}")
            return keywords[:top_n]  # Fallback to first N keywords
        except Exception as e:
            logger.error(f"Priority selection failed: {str(e)}")
            raise

        
    
    def _create_prompt(self, keywords: List[KeywordData], budget: float) -> str:

        try: 

            keyword_sample = [] # converting pydantic objects to simple dictionaries (LLM can't understand Pydantic)
            for kw in keywords:
                keyword_sample.append({
                    "keyword": kw.keyword,
                    "search_volume": kw.search_volume,
                    "competition": kw.competition_level.value,
                    "bid_low": kw.bid_low,
                    "bid_high": kw.bid_high,
                    "cpc": kw.cpc,
                    "concept_groups": kw.concept_groups
                })  
            
            prompt = f"""
    You are an expert Google Ads strategist.

    Here are keywords with their data and semantic concept groups:

    {json.dumps(keyword_sample, indent=2)}

    Organize these keywords into these 5 ad groups:

    - Brand Terms
    - Category Terms  
    - Competitor Terms
    - Location-based Queries
    - Long-Tail Informational Queries

    BUDGET INFORMATION: Total available budget is ${budget}
    Allocate budget proportionally to the ad groups and suggest match types. 
    Eventual goal is to have maximum ROAS(Return on Ad spend) on the keywords that are given

    BUDGET ALLOCATION RULES(order of high to low priority):
    - Total budget is ${budget}
    - Brand Terms: decide what % of budget (highest priority)
    - Category Terms: decide what % of budget
    - Competitor Terms: decide what % of budget
    - Location-based: decide what % of budget
    - Long-tail: decide what % of budget

    Use concept groups to inform classifications:
    - "Brand Names" concept → Brand Terms
    - "Product" concept → Category Terms
    - "Competitors" concept → Competitor Terms
    - "Geography" concept → Location-based Queries
    - Long keywords (4+ words) → Long-Tail Informational

    Return ONLY JSON in the following format. NOTE: The example below shows 
    the structure only - use the ACTUAL keywords provided above:

    {{
    "ad_groups": [
        {{
        "group_name": "Brand Terms",
        "group_type": "brand",
        "budget_allocation": 1000.0,
        "budget_percentage": 50.0,
        "total_keywords": 5,
        "avg_cpc_range": "$1.50 - $3.00",
        "keywords": [
            {{
            "keyword": "example keyword",
            "search_volume": 1000,
            "competition_level": "low",
            "cpc_low": 1.50,
            "cpc_high": 3.00,
            "suggested_match_types": ["exact", "phrase"]
            }}
        ]
        }}
    ]
    }}

    IMPORTANT: Use the actual keyword data provided to calculate the above json format, 
    not the placeholder examples in the format template.
    """
            return prompt
        except Exception as e:
            logger.error(f"Prompt creation failed: {str(e)}")
            raise
    
    async def _call_llm(self, prompt: str) -> str:

        try: 
            # Returns Raw LLM response containing JSON and possibly explanatory text
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Google Ads expert. Return only valid JSON reponses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=5000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI call failed: {str(e)}")
            raise
    
    def _parse_json(self, response: str, budget: float, total_keywords: int) -> SimplifiedDeliverable:
        try:

            logger.info("Starting JSON parsing")

            # Find JSON in potentially mixed response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            # Check if JSON braces were found
            if start == -1 or end == 0:
                logger.error("No JSON braces found in response")
                raise ValueError("No JSON found in response")
                
            json_str = response[start:end]
            json_data = json.loads(json_str)
            logger.info("JSON extracted and parsed successfully")
            
            # Build ad groups with safe field access , basically converting back to pydantic objects
            groups = []
            for group_data in json_data.get("ad_groups", []):
                keywords = []
                for kw in group_data.get("keywords", []):
                    keywords.append(SimpleKeyword(
                        keyword=kw.get("keyword", ""),
                        search_volume=kw.get("search_volume", 0),
                        competition_level=kw.get("competition_level", "medium"),
                        cpc_low=kw.get("cpc_low", 0.0),
                        cpc_high=kw.get("cpc_high", 0.0),
                        suggested_match_types=kw.get("suggested_match_types", ["broad"])
                    ))
                
                groups.append(SimpleAdGroup(
                    group_name=group_data.get("group_name", "Unknown Group"),
                    group_type=group_data.get("group_type", "category"),
                    keywords=keywords,
                    budget_allocation=group_data.get("budget_allocation", 0.0),
                    budget_percentage=group_data.get("budget_percentage", 0.0),
                    total_keywords=group_data.get("total_keywords", len(keywords)),
                    avg_cpc_range=group_data.get("avg_cpc_range", "$0.00 - $0.00")
                ))

            logger.info(f"Successfully created {len(groups)} ad groups")
            
            return SimplifiedDeliverable(
                ad_groups=groups,
                total_budget=json_data.get("total_budget", budget),
                total_keywords_used=json_data.get("total_keywords_used", total_keywords),
                budget_summary=json_data.get("budget_summary", {"brand": 50, "category": 35, "competitor": 15}),
                processing_time=0.0
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed - invalid JSON: {str(e)}")
            return self._create_fallback(budget, total_keywords)
        except ValueError as e:
            logger.error(f"JSON structure error: {str(e)}")
            return self._create_fallback(budget, total_keywords)
        except KeyError as e:
            logger.error(f"Missing required field: {str(e)}")
            return self._create_fallback(budget, total_keywords)

    def _create_fallback(self, budget: float, total_keywords: int) -> SimplifiedDeliverable:

        logger.warning("Creating fallback response")

        """Simple fallback when parsing fails"""
        fallback_group = SimpleAdGroup(
            group_name="Parsing Failed",
            group_type="error",
            keywords=[],
            budget_allocation=budget,
            budget_percentage=100.0,
            total_keywords=0,
            avg_cpc_range="$0.00 - $0.00"
        )
        
        return SimplifiedDeliverable(
            ad_groups=[fallback_group],
            total_budget=budget,
            total_keywords_used=total_keywords,
            budget_summary={"error": 100},
            processing_time=0.0
        )
