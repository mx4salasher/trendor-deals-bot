import aiohttp
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36"
    )
}


async def scrape_product(url):

    try:

        async with aiohttp.ClientSession(
            headers=HEADERS
        ) as session:

            async with session.get(
                url,
                timeout=15,
                allow_redirects=True
            ) as response:

                if response.status != 200:
                    print(
                        "Product page failed:",
                        response.status,
                        url
                    )
                    return None

                html = await response.text()


        soup = BeautifulSoup(
            html,
            "html.parser"
        )


        title = None
        price = None
        image = None


        # Product JSON data
        scripts = soup.find_all(
            "script",
            type="application/ld+json"
        )


        for script in scripts:

            try:

                data = json.loads(
                    script.string
                )


                if isinstance(data, dict):

                    if data.get("@type") == "Product":

                        title = data.get(
                            "name"
                        )


                        img = data.get(
                            "image"
                        )


                        if isinstance(img, list):
                            image = img[0]

                        else:
                            image = img



                        offers = data.get(
                            "offers"
                        )


                        if isinstance(
                            offers,
                            dict
                        ):
                            price = offers.get(
                                "price"
                            )


                        break


            except Exception:
                pass



        # Title fallback
        if not title:

            title_tag = soup.find(
                "title"
            )

            if title_tag:
                title = title_tag.text.strip()



        # Image fallback
        if not image:

            img = soup.find(
                "img"
            )

            if img and img.get(
                "src"
            ):
                image = img.get(
                    "src"
                )



        if image:

            image = urljoin(
                url,
                image
            )



        if not title:

            title = "🔥 Special Deal"



        if not price:

            price = "N/A"



        return {

            "title": title,

            "price": str(price),

            "image": image
            or
            "https://via.placeholder.com/400",

            "link": url

        }



    except Exception as e:

        print(
            "Scraper Error:",
            e
        )

        return None