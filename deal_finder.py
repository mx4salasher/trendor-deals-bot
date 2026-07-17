import random, asyncio, aiohttp
from bs4 import BeautifulSoup
from scraper import scrape_product
import storage

STORES = {
    "amazon": "https://www.amazon.in/deals",
    "flipkart": "https://www.flipkart.com/offers",
    "myntra": "https://www.myntra.com/shop",
    "ajio": "https://www.ajio.com/s/70-percent-off-3554-67351",
    "nykaa": "https://www.nykaa.com/offers"
}

LINK_SEL = {
    "amazon": "a.a-link-normal",
    "flipkart": "a._1fQZEK",
    "myntra": "a.product-base-link",
    "ajio": "a.item",
    "nykaa": "a.css-1rd94et"
}

HEADERS = {"User-Agent": "Mozilla/5.0"}

async def get_links(session, store, url):
    links = []
    try:
        async with session.get(url, headers=HEADERS, timeout=15) as r:
            html = await r.text()
        for a in BeautifulSoup(html, "lxml").select(LINK_SEL.get(store, ""))[:5]:
            href = a.get("href")
            if href and not href.startswith("http"):
                href = f"https://{store}.com{href}"
            if href and not storage.is_duplicate(href):
                links.append(href)
    except Exception as e:
        print(f"[GET_LINKS ERROR {store}] {e}")
    return links

async def find_deals():
    deals = []
    async with aiohttp.ClientSession() as session:
        for store, url in random.sample(list(STORES.items()), len(STORES)):
            try:
                for link in await get_links(session, store, url):
                    p = await scrape_product(link)
                    if p and p["discount"] >= 25: # sirf 25%+ wale deals
                        deals.append(p)
                        break
                await asyncio.sleep(1)
            except Exception as e:
                print(f"[STORE ERROR {store}] {e}")
                continue
    return sorted(deals, key=lambda x: x["discount"], reverse=True)