"""
config.py
Central configuration for Trendora Deals Bot V2
"""

import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# Telegram
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")

# =========================
# API Keys
# =========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EARNKARO_TOKEN = os.getenv("EARNKARO_TOKEN")

# =========================
# Auto Posting
# =========================

AUTO_POST_INTERVAL = 20      # minutes
MAX_RETRY = 3
REQUEST_TIMEOUT = 20

# =========================
# Deal Filters
# =========================

MIN_DISCOUNT = 25
MAX_DEALS_PER_RUN = 5

# =========================
# Image Settings
# =========================

OUTPUT_FOLDER = "instagram_ready"

# =========================
# Supported Stores
# =========================

SUPPORTED_STORES = [
    "amazon",
    "flipkart",
    "myntra",
    "ajio",
    "meesho",
    "shopsy",
    "nykaa",
    "croma",
    "boat",
    "tatacliq",
    "reliancedigital",
    "dotandkey",
    "minimalist",
    "thedermaco",
    "mcaffeine",
    "themancompany",
    "puma",
    "adidas",
    "healthkart",
]