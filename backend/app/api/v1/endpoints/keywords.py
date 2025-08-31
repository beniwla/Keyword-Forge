from fastapi import APIRouter, HTTPException
from app.models.requests import KeywordResearchRequest
from app.models.responses import KeywordResponse
from app.models.ad_groups import FinalKeywordResponse
from app.services.base_keyword_service import BaseKeywordService
from app.services.llm_service import LLMService
from .utils import read_config_yaml
import time
import logging

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/search", response_model=FinalKeywordResponse)
async def research_keywords(request: KeywordResearchRequest):


    """Main endpoint for keywords search"""
    start_time = time.time()
    
    try:
        logger.info(f"New keyword research request for website: {request.competitor_website}")
        logger.info(f"Request budget: ${request.search_ads_budget}")
        
        # Use your BaseKeywordService to orchestrate all APIs
        # Step 1: Generating Keywords
        logger.info("Starting keyword extraction")
        base_service = BaseKeywordService()
        keywords = await base_service.extract_all_keywords(request)
        
        processing_time = time.time() - start_time
        logger.info(f"Keyword extraction completed: {len(keywords)} keywords in {processing_time:.1f}s")
        
        # return KeywordResponse(
        #     total_keywords=len(keywords),
        #     filtered_keywords=len(keywords),  # Already filtered by min_search_volume=500
        #     keywords=keywords,
        #     processing_time=round(processing_time, 2)
        # )


        # Step 2: LLM Integration
        logger.info("Starting LLM service for ad group creation")
        llm_service = LLMService()
        deliverable = await llm_service.create_ad_groups(keywords, request)


        # Step 3: Return complete response
        total_time = time.time() - start_time
        logger.info(f"Research completed successfully in {total_time:.1f}s total")
        logger.info(f"Created {len(deliverable.ad_groups)} ad groups")
        
        return FinalKeywordResponse(
            total_keywords=len(keywords),
            processing_time=processing_time,  # Just extraction time
            deliverable=deliverable  # LLM result with its own processing_time
        )
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"Keyword research failed after {total_time:.1f}s: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Keyword extraction failed: {str(e)}") # will give generic server error without this


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {"status": "healthy", "message": "Keyword service is running"}


@router.post("/search-from-config", response_model=FinalKeywordResponse)
async def research_keywords_from_config():
    """Research keywords using config.yaml file"""
    logger.info("Starting keyword research from config file")
    
    try:
        # Read config.yaml
        config_data = read_config_yaml()
        logger.info(f"Config loaded: {config_data.get('brand_website')}")
        
        # Convert to request model
        request = KeywordResearchRequest(**config_data)
        
        # Use your existing research_keywords function
        return await research_keywords(request)
        
    except Exception as e:
        logger.error(f"Config-based research failed: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Config processing failed: {str(e)}")