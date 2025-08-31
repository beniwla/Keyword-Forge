import os
from dotenv import load_dotenv

load_dotenv()

KEYWORDS_FOR_SITE_API_AUTH = os.getenv("KEYWORDS_FOR_SITE_API_AUTH")
KEYWORDS_FOR_KEYWORDS_API_AUTH = os.getenv("KEYWORDS_FOR_KEYWORDS_API_AUTH") 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")