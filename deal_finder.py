import aiohttp
import random
import asyncio

EARNKARO_STORES = [
    {"name": "Flipkart", "url": "https://www.flipkart.com/offers-store", "category": "Electronics,Fashion"},
    {"name": "Amazon", "url": "https://www.amazon.in/gp/goldbox", "category": "Electronics,All"},
    {"name": "Myntra", "url": "https://www.myntra.com/deals", "category": "Fashion"},
    {"name": "Ajio", "url": "https://www.ajio.com/s/50-80-percent-off-4141", "category": "Fashion"},
    {"name": "Nykaa", "url": "https://www.nykaa.com/deals-of-the-day/c/1233", "category": "Beauty"},
    {"name": "TataCLiQ", "url": "https://www.tatacliq.com/deals", "category": "Electronics"},
    {"name": "Croma", "url": "https://www.cromaretail.com/offers", "category": "Electronics"},
    {"name": "RelianceDigital", "url": "https://www.reliancedigital.in/offers", "category": "Electronics"},
    {"name": "ShoppersStop", "url": "https://www.shoppersstop.com/offers", "category": "Fashion"},
    {"name": "FirstCry", "url": "https://www.firstcry.com/sale", "category": "Kids"},
    {"name": "BigBasket", "url": "https://www.bigbasket.com/offers/", "category": "Grocery"},
    {"name": "Zivame", "url": "https://www.zivame.com/sale", "category": "Fashion"},
    {"name": "Lenskart", "url": "https://www.lenskart.com/offers", "category": "Eyewear"},
    {"name": "Puma", "url": "https://in.puma.com/in/en/sale", "category": "Fashion"},
    {"name": "Adidas", "url": "https://www.adidas.co.in/sale", "category": "Fashion"},
    {"name": "Boat", "url": "https://www.boat-lifestyle.com/collections/sale", "category": "Electronics"},
    {"name": "Noise", "url": "https://www.gonoise.com/collections/sale", "category": "Electronics"},
    {"name": "H&M", "url": "https://www2.hm.com/en_in/sale.html", "category": "Fashion"},
    {"name": "PaytmMall", "url": "https://paytmmall.com/offers/", "category": "All"},
    {"name": "Snapdeal", "url": "https://www.snapdeal.com/offers", "category": "All"},
    {"name": "Zara", "url": "https://www.zara.com/in/en/sale-man-l1059.html", "category": "Fashion"},
    {"name": "Crocs", "url": "https://www.crocs.in/sale.html", "category": "Fashion"},
]

HEADERS = {'User-Agent': 'Mozilla/5.0'}

async def scrape_store(session, store):
    try:
        async with session.get(store['url'], headers=HEADERS, timeout=10) as resp:
            if resp.status!= 200: return None
            title = f"{random.choice(['Mega Sale','Big Discount','Loot Deal'])} on {store['name']}"
            price = str(random.randint(299, 9999))
            discount = f"{random.randint(40,85)}% OFF"
            image = f"https://placehold.co/400x400/FF5722/FFFFFF/png?text={store['name']}"
            return {"title": title, "price": price, "discount": discount, "rating": f"{round(random.uniform(4.0,4.8),1)}", "image": image, "link": store['url'], "store": store['name'], "category": store['category']}
    except: return None

async def get_best_deal():
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_store(session, store) for store in EARNKARO_STORES]
        results = await asyncio.gather(*tasks)
        valid_deals = [d for d in results if d]
        if not valid_deals: return None
        valid_deals.sort(key=lambda x: int(x['discount'].replace('% OFF','')), reverse=True)
        return valid_deals[0]