import aiohttp
import os
EARNKARO_API = "https://api.earnkaro.com/v1/affiliate/link"

async def get_affiliate_link(url):
    api_key = os.getenv("EARNKARO_API_KEY")
    if not api_key: return url
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"url": url, "api_key": api_key}
            async with session.post(EARNKARO_API, json=payload, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("affiliate_url", url)
    except: pass
    return url