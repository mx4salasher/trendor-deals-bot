"""
scraper.py
Safely scrapes basic product data from Amazon or Flipkart URLs.
Optimized to handle generic headers to minimize blocks.
"""
import re
import requests
from bs4 import BeautifulSoup

def scrape_product(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch site, status code: {response.status_code}")
        
    soup = BeautifulSoup(response.content, "html.parser")
    title, price, mrp, image_url = "Product", 0.0, 0.0, ""
    
    if "amazon" in url.lower():
        # Title logic
        title_el = soup.find(id="productTitle")
        if title_el:
            title = title_el.get_text().strip()
            
        # Price logic
        price_el = soup.find("span", {"class": "a-price-whole"})
        if price_el:
            price_text = re.sub(r"[^\d]", "", price_el.get_text())
            if price_text:
                price = float(price_text)
                
        # MRP logic
        mrp_el = soup.find("span", {"class": "a-size-small a-color-secondary a-line-through"})
        if not mrp_el:
             mrp_el = soup.find("span", {"class": "basisPrice"})
        if mrp_el:
            mrp_text = re.sub(r"[^\d]", "", mrp_el.get_text())
            if mrp_text:
                mrp = float(mrp_text)
        else:
            mrp = price  # Default fallback if no strikeout price
            
        # Image
        img_el = soup.find("img", {"id": "landingImage"})
        if img_el:
            image_url = img_el.get("src", "")
            
    elif "flipkart" in url.lower():
        # Title
        title_el = soup.find("span", {"class": "VU-ZEg"}) # Common FK Product title class
        if not title_el:
            title_el = soup.find("h1")
        if title_el:
            title = title_el.get_text().strip()
            
        # Price
        price_el = soup.find("div", {"class": "Nx9b9A"})
        if not price_el:
            price_el = soup.find("div", {"class": "_30jeq3 _16Jk6d"})
        if price_el:
            price_text = re.sub(r"[^\d]", "", price_el.get_text())
            if price_text:
                price = float(price_text)
                
        # MRP
        mrp_el = soup.find("div", {"class": "yYWSg9"})
        if not mrp_el:
            mrp_el = soup.find("div", {"class": "_3I9_g3 _2p61b2"})
        if mrp_el:
            mrp_text = re.sub(r"[^\d]", "", mrp_el.get_text())
            if mrp_text:
                mrp = float(mrp_text)
        else:
            mrp = price
            
        # Image
        img_el = soup.find("img", {"class": "DByo73"})
        if not img_el:
            img_el = soup.find("img", {"class": "_396cs4"})
        if img_el:
            image_url = img_el.get("src", "")
            
    if mrp < price:
        mrp = price
        
    return {
        "title": title,
        "price": price,
        "mrp": mrp,
        "image_url": image_url
    }