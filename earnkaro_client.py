import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://ekaro-api.affiliaters.in/api/converter/public"


async def get_affiliate_link(url):
    api_key = os.getenv("EARNKARO_API_KEY")

    print("\n========== EARNKARO DEBUG ==========")
    print("Original URL:", url)

    if not api_key:
        print("❌ API KEY Missing")
        return url

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "deal": url,
        "convert_option": "convert_only"
    }

    print("Payload Sent:", payload)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                API_URL,
                headers=headers,
                json=payload
            ) as resp:

                print("Status Code:", resp.status)

                data = await resp.json()

                print("EarnKaro Response:")
                print(data)

                if resp.status == 200 and data.get("success") == 1:

                    affiliate_link = data.get("data")

                    print("✅ Affiliate Link Generated:")
                    print(affiliate_link)

                    print("====================================\n")

                    return affiliate_link

                else:
                    print("❌ Affiliate conversion failed")
                    print("Returning original URL")

                    print("====================================\n")

                    return url

    except Exception as e:
        print("❌ EarnKaro Error:", e)
        print("Returning original URL")
        print("====================================\n")

        return url