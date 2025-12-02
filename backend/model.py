import os
from phi.model.openai import OpenAIChat
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env from backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(backend_dir, '.env'))

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")

def get_model():
    if not OPENROUTER_API_KEY:
        # Fallback to OpenAI if OpenRouter key is missing but OpenAI key exists
        if os.getenv("OPENAI_API_KEY"):
            logger.info("Using OpenAI API")
            return OpenAIChat(id="gpt-4o")
        raise ValueError("OPENROUTER_API_KEY or OPENAI_API_KEY must be set.")

    logger.info(f"Using OpenRouter with model: {OPENROUTER_MODEL}")
    
    # OpenRouter requires specific headers
    return OpenAIChat(
        id=OPENROUTER_MODEL,
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        extra_headers={
            "HTTP-Referer": "http://localhost:3000",  # Required by OpenRouter
            "X-Title": "recipe AI Multi-Agent System"  # Optional but recommended
        }
    )
