import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve the DATABASE_URL environment variable
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL")
REDIS = os.getenv("REDIS")
EXTERNAL_LIBRARY_LEVEL_LOG = os.getenv("EXTERNAL_LIBRARY_LEVEL_LOG")
LOG_LEVEL = os.getenv("LOG_LEVEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
