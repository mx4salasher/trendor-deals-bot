import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from scraper import scrape_product


EARNKARO_STORES = [
    {"name": "Flipkart", "url": "https://www.flipkart.com/offers-store", "category": "Electronics,Fashion"},
    {"name": "Amazon", "url": "https://www.amazon.in/gp/goldbox", "category": "Electronics,All"},
    {"name": "Myntra", "url": "https://www.myntra.com/deals", "category": "Fashion"},
    {"name": "Ajio", "url": "https://www.ajio.com/s/50-80-percent-off-4141", "category": "Fashion"},
    {"name": "Nykaa", "url": "https://www.nykaa.com/deals-of-the-day/c/1233", "category": "Beauty"},
    {"name": "TataCLiQ", "url": "https://www.tatacliq.com/deals", "category": "Electronics"},
    {"name": "Croma", "url": "https://www.croma.com/offers", "category": "Electronics"},
    {"name": "RelianceDigital", "url": "https://www.reliancedigital.in/offers", "category": "Electronics"},
    {"name": "Boat", "url": "https://www.boat-lifestyle.com/collections/sale", "category": "Electronics"},
    {"name": "Noise", "url": "https://www.gonoise.com/collections/sale", "category": "Electronics"},
    {"name": "Puma", "url": "https://in.puma.com/in/en/sale", "category": "Fashion"},
    {"name": "Adidas", "url": "https://www.adidas.co.in/sale", "category": "Fashion"},
    {"name": "H&M", "url": "https://www2.hm.com/en_in/sale.html", "category": "Fashion"},
    {"name": "Zara", "url": "https://www.zara.com/in/en/sale", "category": "Fashion"},
    {"name": "Crocs", "url": "https://www.crocs.in/sale.html", "category": "Fashion"},
    {"name": "FirstCry", "url": "https://www.firstcry.com/sale", "category": "Kids"},
    {"name": "BigBasket", "url": "https://www.bigbasket.com/offers/", "category": "Grocery"},
    {"name": "Lenskart", "url": "https://www.lenskart.com/offers", "category": "Eyewear"},
    {"name": "Zivame", "url": "https://www.zivame.com/sale", "category": "Fashion"},
    {"name": "Snapdeal", "url": "https://www.snapdeal.com/offers", "category": "All"},
    {"name": "PaytmMall", "url": "https://paytmmall.com/offers/", "category": "All"},
    {"name": "Meesho", "url": "https://www.meesho.com", "category": "All"},
]


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}



async def extract_product_links(session, store):

    links = []

    try:

        async with session.get(
            store["url"],
            headers=HEADERS,
            timeout=15
        ) as response:


            if response.status != 200:
                return []


            html = await response.text()


        soup = BeautifulSoup(
            html,
            "html.parser"
        )


        for a in soup.find_all(
            "a",
            href=True
        ):

            href = a["href"]


            if (
                "/dp/" in href
                or "/product" in href
                or "/p/" in href
                or "/buy" in href
            ):

                full = urljoin(
                    store["url"],
                    href
                )


                if full not in links:
                    links.append(full)



        return links[:3]


    except Exception as e:

        print(
            "Extract error:",
            store["name"],
            e
        )

        return []



async def scan_store(session, store):

    deals = []


    links = await extract_product_links(
        session,
        store
    )


    for link in links:

        product = await scrape_product(
            link
        )


        if product:

            product["store"] = store["name"]

            product["category"] = store["category"]

            product["discount"] = "Best Deal"

            product["rating"] = "4.5"


            deals.append(
                product
            )


    return deals



async def get_best_deal():

    async with aiohttp.ClientSession() as session:


        tasks = [

            scan_store(
                session,
                store
            )

            for store in EARNKARO_STORES

        ]


        results = await asyncio.gather(
            *tasks
        )


    all_deals = []


    for item in results:

        all_deals.extend(
            item
        )


    if not all_deals:

        return None


    return all_deals[0]