import asyncio
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
        print("❌ EARNKARO_API_KEY missing")
        print("====================================\n")
        return url


    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


    payload = {
        "deal": url,
        "convert_option": "convert_only"
    }


    print("Payload:", payload)


    try:

        timeout = aiohttp.ClientTimeout(total=20)

        async with aiohttp.ClientSession(timeout=timeout) as session:

            async with session.post(
                API_URL,
                headers=headers,
                json=payload
            ) as response:


                print("Status:", response.status)


                try:
                    data = await response.json()

                except Exception:
                    text = await response.text()
                    print("❌ Non JSON Response:", text)

                    return url



                print("Response:", data)



                if response.status != 200:
                    print("❌ API Failed")
                    return url



                if data.get("success") != 1:
                    print("❌ EarnKaro success false")
                    return url



                affiliate_link = data.get("data")


                # Check real URL
                if (
                    isinstance(affiliate_link, str)
                    and affiliate_link.startswith("http")
                ):

                    print("✅ Affiliate Generated:")
                    print(affiliate_link)

                    print("====================================\n")

                    return affiliate_link



                else:

                    print("❌ EarnKaro returned invalid link")
                    print("Using original URL")

                    print("====================================\n")

                    return url



    except asyncio.TimeoutError:

        print("❌ EarnKaro Timeout")
        print("Using original URL")

        print("====================================\n")

        return url



    except Exception as e:

        print("❌ EarnKaro Error:", e)

        print("Using original URL")

        print("====================================\n")

        return url