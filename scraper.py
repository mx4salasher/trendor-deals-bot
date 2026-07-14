"""
scraper.py
Fetches product title, image, MRP (original price) and current selling price
from an Amazon.in or Flipkart product link.

NOTE: E-commerce sites frequently change their HTML structure and actively
block scrapers. If scraping fails, the bot will ask you to enter price
details manually instead of breaking the whole flow.
"""

import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}


def _clean_price(text):
    """Extract a float price from messy text like '₹1,999' or 'MRP: ₹2,499.00'."""
    if not text:
        return None
    match = re.search(r"[\d,]+(?:\.\d+)?", text.replace("\xa0", " "))
    if not match:
        return None
    return float(match.group().replace(",", ""))


def scrape_amazon(url: str):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")

    title_tag = soup.select_one("#productTitle")
    title = title_tag.get_text(strip=True) if title_tag else None

    img_tag = soup.select_one("#landingImage") or soup.select_one("#imgTagWrapperId img")
    image_url = None
    if img_tag:
        image_url = img_tag.get("src") or img_tag.get("data-old-hires")

    price_tag = soup.select_one(".a-price .a-offscreen") or soup.select_one("#priceblock_ourprice")
    price = _clean_price(price_tag.get_text() if price_tag else None)

    mrp_tag = soup.select_one(".a-text-price .a-offscreen")
    mrp = _clean_price(mrp_tag.get_text() if mrp_tag else None)

    return {
        "title": title,
        "image_url": image_url,
        "price": price,
        "mrp": mrp or price,
    }


def scrape_flipkart(url: str):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")

    title_tag = soup.select_one("span.B_NuCI") or soup.select_one("h1 span")
    title = title_tag.get_text(strip=True) if title_tag else None

    img_tag = soup.select_one("img._396cs4") or soup.select_one("img._2r_T1I")
    image_url = img_tag.get("src") if img_tag else None

    price_tag = soup.select_one("div._30jeq3._16Jk6d") or soup.select_one("div._30jeq3")
    price = _clean_price(price_tag.get_text() if price_tag else None)

    mrp_tag = soup.select_one("div._3I9_wc._2p6lqe")
    mrp = _clean_price(mrp_tag.get_text() if mrp_tag else None)

    return {
        "title": title,
        "image_url": image_url,
        "price": price,
        "mrp": mrp or price,
    }


def scrape_product(url: str):
    """Dispatch to the right scraper based on domain. Returns dict or raises."""
    if "amazon." in url:
        data = scrape_amazon(url)
    elif "flipkart." in url:
        data = scrape_flipkart(url)
    else:
        raise ValueError("Sirf Amazon ya Flipkart links supported hain abhi.")

    if not data.get("title") or not data.get("price"):
        raise ValueError(
            "Scraping se poora data nahi mila (website ne block kar diya ho sakta hai). "
            "Manual entry try karo."
        )
    return data
