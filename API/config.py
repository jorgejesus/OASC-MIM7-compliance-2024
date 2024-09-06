import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# Load and set environment variables with defaults if not present
VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG_LEVEL = os.getenv("API_LOG_LEVEL", "INFO").upper()

# Default to INFO if the level is invalid
LOG_LEVEL = LOG_LEVEL if LOG_LEVEL in VALID_LOG_LEVELS else "INFO"
