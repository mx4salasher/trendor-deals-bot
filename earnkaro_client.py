"""
earnkaro_client.py
Trendora bot ke liye EarnKaro link-converter API wrapper.

Environment variable chahiye:
    EARNKARO_TOKEN  -> EarnKaro dashboard se mila hua API token

NOTE: Neeche diya gaya endpoint aur request/response format EarnKaro ke
publicly documented "converter/public" API page ke hisab se hai jo tumne
dikhaya tha. Agar tumhare API dashboard mein exact field names ya
convert_option values alag dikhein (screenshot mein "Request body" section),
toh CONVERT_URL aur payload/response keys neeche update kar dena.
"""

import os
import requests

EARNKARO_TOKEN = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2YTQ2YTQzZGEwODI1YTUyYjNjODEyNzciLCJlYXJua2FybyI6IjU0MDU0NzEiLCJpYXQiOjE3ODQwMzM2NjB9.kmpZ1fycHyP8KLw638uk_eNPlA2OamuhzJy8wkjmFl8")
CONVERT_URL = "https://ekaro-api.affiliaters.in/api/converter/public"


class EarnKaroError(Exception):
    """EarnKaro API se related koi bhi error."""
    pass


def convert_to_affiliate_link(original_url: str, convert_option: str = "convert_only") -> str:
    """
    Ek normal product link ko EarnKaro affiliate (profit) link mein convert karta hai.

    Args:
        original_url: Amazon/Flipkart/etc ka original product link
        convert_option: EarnKaro API ka option (default "convert_only")

    Returns:
        Affiliate link (string)

    Raises:
        EarnKaroError: agar token missing ho, request fail ho, ya response
                       mein affiliate link na mile
    """
    if not EARNKARO_TOKEN:
        raise EarnKaroError("EARNKARO_TOKEN environment variable set nahi hai.")

    headers = {
        "Authorization": f"Bearer {EARNKARO_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "deal": original_url,
        "convert_option": convert_option,
    }

    try:
        response = requests.post(CONVERT_URL, headers=headers, json=payload, timeout=15)
    except requests.RequestException as exc:
        raise EarnKaroError(f"EarnKaro API tak request nahi pahunch payi: {exc}") from exc

    if response.status_code != 200:
        raise EarnKaroError(
            f"EarnKaro API ne error diya (status {response.status_code}): {response.text}"
        )

    data = response.json()

    # NOTE: 'data' key EarnKaro ke sample response ke hisab se hai.
    # Agar tumhare docs mein response ka structure alag ho (jaise
    # data['affiliate_url'] ya data['converted_url']), yahan update karo.
    affiliate_link = data.get("data")

    if not affiliate_link:
        raise EarnKaroError(f"Affiliate link response mein nahi mila: {data}")

    return affiliate_link


def convert_multiple(urls: list[str]) -> dict:
    """
    Multiple links ek saath convert karne ke liye helper.
    Kisi ek link mein error aaye toh baaki process hote rahenge,
    aur error wale links None ke saath return honge.

    Returns:
        {original_url: affiliate_link_or_None}
    """
    results = {}
    for url in urls:
        try:
            results[url] = convert_to_affiliate_link(url)
        except EarnKaroError as exc:
            print(f"[earnkaro_client] Convert fail hua {url} -> {exc}")
            results[url] = None
    return results