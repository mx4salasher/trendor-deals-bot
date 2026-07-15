"""
deal_finder.py
Amazon aur Flipkart ke "deals/offers" listing pages se khud product links
dhundta hai, unhe scraper.py se scrape karta hai, aur ek poora ready-to-post
deal package banata hai (affiliate link + caption + category + image ke saath).

NOTE: Listing pages ka HTML structure Amazon/Flipkart kabhi bhi badal sakte
hain, aur bot-jaisi requests ko block bhi kar sakte hain. Isliye har jagah
try/except hai — agar ek source fail ho, doosra try hota hai. Agar dono fail
ho jayein, find_new_deal() None return karta hai (bot crash nahi karega).
"""

import re
import random
import logging
import requests
from bs4 import BeautifulSoup

import scraper
import storage
import earnkaro_client
import ai_client

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}

MIN_DISCOUNT_PERCENT = 25  # isse kam discount wale deals skip ho jayenge

AMAZON_DEALS_URL = "https://www.amazon.in/deals"
FLIPKART_OFFERS_URL = "https://www.flipkart.com/offers-list/deal-of-the-day"


def _find_amazon_links(limit=15):
    links = []
    try:
        resp = requests.get(AMAZON_DEALS_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.select("a[href*='/dp/']"):
            href = a.get("href")
            if not href:
                continue
            match = re.search(r"/dp/([A-Z0-9]{10})", href)
            if match:
                full_url = f"https://www.amazon.in/dp/{match.group(1)}"
                if full_url not in links:
                    links.append(full_url)
            if len(links) >= limit:
                break
    except Exception as e:
        logger.warning(f"Amazon deals page fetch fail hui: {e}")
    return links


def _find_flipkart_links(limit=15):
    links = []
    try:
        resp = requests.get(FLIPKART_OFFERS_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.select("a[href*='/p/']"):
            href = a.get("href")
            if not href:
                continue
            full_url = "https://www.flipkart.com" + href.split("?")[0]
            if full_url not in links:
                links.append(full_url)
            if len(links) >= limit:
                break
    except Exception as e:
        logger.warning(f"Flipkart offers page fetch fail hui: {e}")
    return links


def _discount_percent(mrp, price):
    if not mrp or mrp <= 0:
        return 0
    return round((mrp - price) / mrp * 100)


def find_new_deal():
    """
    Ek naya (pehle post na hua) achha-discount wala deal dhundhta hai.
    Return: dict with title, image_url, price, mrp, discount, source_url,
            affiliate_link, category, caption  --  ya None agar kuch na mile.
    """
    candidate_links = _find_amazon_links() + _find_flipkart_links()
    random.shuffle(candidate_links)

    for url in candidate_links:
        if storage.is_already_posted(url):
            continue

        try:
            data = scraper.scrape_product(url)
        except Exception as e:
            logger.info(f"Scrape skip {url}: {e}")
            continue

        discount = _discount_percent(data["mrp"], data["price"])
        if discount < MIN_DISCOUNT_PERCENT:
            continue

        try:
            affiliate_link = earnkaro_client.convert_to_affiliate_link(url)
        except earnkaro_client.EarnKaroError as e:
            logger.warning(f"EarnKaro convert fail {url}: {e}")
            continue

        category = ai_client.ai_classify_category(data["title"])
        caption = ai_client.ai_generate_caption(
            data["title"], data["price"], data["mrp"], discount, affiliate_link
        )

        return {
            "title": data["title"],
            "image_url": data["image_url"],
            "price": data["price"],
            "mrp": data["mrp"],
            "discount": discount,
            "source_url": url,
            "affiliate_link": affiliate_link,
            "category": category,
            "caption": caption,
        }

    return None  # koi naya achha deal nahi mila is baar