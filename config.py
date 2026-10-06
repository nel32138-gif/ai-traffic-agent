import os
from dotenv import load_dotenv

load_dotenv()

RESULTS = int(
    os.getenv("RESULTS", "10")
)

SEARCH_LIMIT = int(
    os.getenv("SEARCH_LIMIT", "100")
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
)

USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
    "AppleWebKit/605.1.15 "
    "Version/18.0 Mobile/15E148 Safari/604.1"
)
