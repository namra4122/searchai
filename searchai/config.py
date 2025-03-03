"""
Configuration settings for the SearchAI application.
Handles environment variables and application settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from crewai import LLM

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = os.path.join(BASE_DIR, 'generated_output')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Create necessary directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# API Keys
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Database Configuration
POSTGRES_URI = os.getenv('POSTGRES_URI')

# Application Settings
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = os.path.join(BASE_DIR, 'generated_output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Search Settings
MAX_CONCURRENT_SEARCHES = 1
SEARCH_TIMEOUT = 60  # seconds

# Model settings
CREWAI_GEMINI_MODEL = "gemini/gemini-1.5-pro-latest"
GEMINI_MODEL = "gemini-2.0-flash-thinking-exp-01-21"

def validate_config():
    """
    Validate that all required configuration variables are set.
    """
    required_vars = {
        'SERPER_API_KEY': SERPER_API_KEY,
        'GEMINI_API_KEY': GEMINI_API_KEY,
        'POSTGRES_URI': POSTGRES_URI
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please set these variables in your .env file"
        )