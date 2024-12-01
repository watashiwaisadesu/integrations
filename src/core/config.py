import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve the DATABASE_URL environment variable
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL")
INSTAGRAM_APP_NAME = os.getenv("INSTAGRAM_APP_NAME")
INSTAGRAM_BUSINESS_LOGIN_EMBED_URL = os.getenv("INSTAGRAM_BUSINESS_LOGIN_EMBED_URL")
INSTAGRAM_APP_ID = os.getenv("INSTAGRAM_APP_ID")
INSTAGRAM_APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET")
COOKIES_FILE = 'cookies.pkl'