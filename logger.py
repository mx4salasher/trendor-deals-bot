"""
logger.py
Central logging system for Trendora Deals Bot V2
"""

import logging
import os

LOG_FOLDER = "logs"
os.makedirs(LOG_FOLDER, exist_ok=True)

LOG_FILE = os.path.join(LOG_FOLDER, "trendora.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)


def get_logger(name):
    return logging.getLogger(name)