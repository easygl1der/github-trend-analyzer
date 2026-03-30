import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:18000")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Default Parameters
DEFAULT_LANGUAGE = "all"
DEFAULT_SINCE = "daily"
DEFAULT_LIMIT = 10

# Report Output
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")

# Ensure reports directory exists
os.makedirs(REPORTS_DIR, exist_ok=True)
