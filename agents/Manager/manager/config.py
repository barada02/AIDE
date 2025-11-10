"""
Configuration for the Lead Manager Agent.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Model configuration
MODEL = os.getenv("MODEL", "gemini-2.0-flash-lite")


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")
CLOUD_PROJECT_ID = os.getenv("CLOUD_PROJECT_ID", "")
CLOUD_PROJECT_REGION = os.getenv("CLOUD_PROJECT_REGION", "")