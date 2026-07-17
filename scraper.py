import aiohttp
import asyncio
import re
import time
import json
import os
from bs4 import BeautifulSoup

MAX_DEALS = 50
DB_FILE = "db/deals.json"

def _load():
    if not os.path.exists(DB_FILE):
        return {"posted_links": [], "deals": []}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    os.makedirs("db", exist_ok=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_deal(deal):
    data = _load()
    data["posted_links"] = data["posted_links"][-MAX_DEALS:]
    deal["posted_time"] = int(time.time())
    data["deals"].append(deal)
    _save(data)

def get_stats():
    data = _load()
    return {
        "total_posted": len(data["posted_links"]),
        "last_deal": data["deals"][-1] if data["deals"] else None
    }

# 20+ Store ke selectors
STORE_SELECTORS = {
    "flipkart.com": {
        "title": "span.B_NuCI",
        "price": "div._30jeq3._16Jk6d",
        "image": "img._396cs4._3exPp9"
    },
    "amazon.in": {
        "title": "span#productTitle",
        "price": "span.a-offscreen",
        "image": "img#landingImage"
    },
    "myntra.com": {
        "title": "h1.pdp-name",
        "price": "span.pdp-price",
        "image": "img.image-grid-image"
    },
    "ajio.com": {
        "title": "div.prod-name",
        "price": "span.prod-sp",
        "image": "img.imgHolder"
    },
    "nykaa.com": {
        "title": "div.css-1gc4x8i",
        "price": "span.css-1jczs8",
        "image": "img.css-1b0uizb"
    },
    "tatacliq.com": {
        "title": "div.pdp__heading",
        "price": "div.TdT8",
        "image": "img.ProductDetailImage__image"
    },
    "reliancedigital.in": {
        "title": "h1.pdp__productName",
        "price": "div.pdp__price",
        "image": "img.img-responsive"
    },
    "croma.com": {
        "title": "h1.cp-product-title",
        "price": "span.amount",
        "image": "img.img-fluid"
    },
    "boat-lifestyle.com": {
        "title": "h1.product__title",
        "price": "span.price-item",
        "image": "img.product__media-item"
    },
    "noise.com": {
        "title": "h1.product-title",
        "price": "span.price",
        "image": "img.product-gallery__image"
    },
    "puma.com": {
        "title": "h1.pdp-name",
        "price": "div.pdp-price",
        "image": "img.pdp-image"
    },
    "nike.com": {
        "title": "h1.product-title",
        "price": "div.product-price",
        "image": "img.product-image"
    },
    "zara.com": {
        "title": "h1.product-detail-info__header-name",
        "price": "span.money-amount",
        "image": "img.media-image"
    },
    "hm.com": {
        "title": "h1.product-item-headline",
        "price": "span.price-value",
        "image": "img.product-detail-main-image"
    },
    "firstcry.com": {
        "title": "div.prod-title",
        "price": "div.prod-price",
        "image": "img.img-responsive"
    },
    "bigbasket.com": {
        "title": "h1.description",
        "price": "span.discnt-price",
        "image": "img.img-responsive"
    },
    "zepto.com": {
        "title": "h1.font-bold",
        "price": "div.text-xl",
        "image": "img.object-contain"
    },
    "blinkit.com": {
        "title": "div.ProductName__TextContainer",
        "price": "div.Price__Container",
        "image": "img.Image__StyledImage"
    },
    "swiggy.com/instamart": {
        "title": "h1._1sW0X",
        "price": "span._1sW0X",
        "image": "img._1sW0X"
    },
    "meesho.com": {
        "title": "h1.ProductName",
        "price": "h4.Price",
        "image": "img.ProductImage"
    }
}

async def scrape_product(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=15, allow_redirects=True) as response:
                html = await response.text()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Detect store
        selectors = None
        for store in STORE_SELECTORS:
            if store in url:
                selectors = STORE_SELECTORS[store]
                break
        
        if selectors:
            title_tag = soup.select_one(selectors["title"])
            price_tag = soup.select_one(selectors["price"])
            img_tag = soup.select_one(selectors["image"])
            
            title = title_tag.text.strip() if title_tag else "Product"
            price = price_tag.text.strip() if price_tag else "₹N/A"
            image = img_tag['src'] if img_tag and img_tag.has_attr('src') else "https://via.placeholder.com/300"
        else:
            # Generic fallback
            title = soup.find('title').text.strip() if soup.find('title') else "Product"
            price = "₹N/A"
            image = "https://via.placeholder.com/300"
        
        return {
            "title": title,
            "price": price,
            "image": image,
            "link": url
        }
    
    except Exception as e:
        print(f"Scraping error: {e}")
        return {
            "title": "Product",
            "price": "₹N/A", 
            "image": "https://via.placeholder.com/300",
            "link": url
        }