import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CREDENTIALS_DIR = DATA_DIR / "credentials"
OUTPUT_DIR = DATA_DIR / "output"

# Create directories if they don't exist
CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AMAZON_EMAIL = os.getenv("AMAZON_EMAIL")
AMAZON_PASSWORD = os.getenv("AMAZON_PASSWORD")

FIREBASE_CREDENTIALS_PATH = CREDENTIALS_DIR / "firebase_credentials.json"
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")

COOKIES_PATH = CREDENTIALS_DIR / "amazon_cookies.pkl"
BESTSELLER_TOPICS_PATH = DATA_DIR / "bestseller_topics.txt"
PRODUCT_LINKS_PATH = OUTPUT_DIR / "product_links.txt"
AFFILIATE_LINKS_PATH = OUTPUT_DIR / "affiliate_links.txt"
ERROR_LOG_PATH = OUTPUT_DIR / "errors.log"
