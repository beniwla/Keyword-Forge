from fastapi import APIRouter
from app.api.v1.endpoints import keywords

api_router = APIRouter()
api_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
