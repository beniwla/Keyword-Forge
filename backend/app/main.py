from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.config import ALLOWED_ORIGINS 

app = FastAPI(
    title="Keyword Search API",
    description="Automated keyword search",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Your React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Keyword Search API is running"}


# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# run the command from where .env file is present