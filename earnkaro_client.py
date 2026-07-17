import aiohttp, os
from tenacity import retry, stop_after_attempt, wait_exponential

API = "https://api.earnkaro.com/v1/link"
KEY = os.getenv("EARNKARO_API_KEY")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2,max=10))
async def get_affiliate_link(url):
    if not KEY or KEY == "your-earnkaro-api-key":
        return url  # agar key nahi hai toh original link hi return kar de
    
    async with aiohttp.ClientSession() as s:
        try:
            async with s.post(API, json={"url":url,"api_key":KEY}, timeout=10) as r:
                data = await r.json()
                return data.get("affiliate_url", url)
        except Exception as e:
            print(f"[EARNKARO ERROR] {e}")
            return url