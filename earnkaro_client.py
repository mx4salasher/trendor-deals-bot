import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://ekaro-api.affiliaters.in/api/converter/public"

async def get_affiliate_link(url):
    api_key = os.getenv("EARNKARO_API_KEY")

    if not api_key:
        print("API KEY Missing")
        return url

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "deal": url,
        "convert_option": "convert_only"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, headers=headers, json=payload) as resp:

                print("Status:", resp.status)

                data = await resp.json()

                print(data)

                if resp.status == 200 and data.get("success") == 1:
                    return data["data"]

                return url

    except Exception as e:
        print("EarnKaro Error:", e)
        return url