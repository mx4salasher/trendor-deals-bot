import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://ekaro-api.affiliaters.in/api/converter/public"


async def get_affiliate_link(url):

    api_key = os.getenv("EARNKARO_API_KEY")

    if not api_key:
        print("❌ EarnKaro API Key Missing")
        return url

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "deal": url,
        "convert_option": "convert_only"
    }

    print("\n========== EARNKARO DEBUG ==========")
    print("Original URL:", url)

    try:

        timeout = aiohttp.ClientTimeout(total=20)

        async with aiohttp.ClientSession(timeout=timeout) as session:

            async with session.post(
                API_URL,
                headers=headers,
                json=payload
            ) as resp:

                print("Status Code:", resp.status)

                data = await resp.json()

                print("Response:", data)


                affiliate_url = data.get("data")


                # Check real affiliate link
                if (
                    data.get("success") == 1
                    and isinstance(affiliate_url, str)
                    and affiliate_url.startswith("http")
                ):

                    print("✅ Affiliate Link Generated")
                    print(affiliate_url)

                    return affiliate_url


                print("❌ Affiliate Link Not Available")
                print("Using Original Link")

                return url


    except Exception as e:

        print("❌ EarnKaro Error:", e)
        return url