"""
ai_client.py
Free AI layer using Groq's API (OpenAI-compatible, generous free tier,
no credit card needed — sign up at https://console.groq.com).

Every function here has a safe fallback: if the AI call fails (no internet,
rate-limited, bad key), the bot falls back to the old template/keyword
behaviour instead of breaking.

Environment variable required:
  GROQ_API_KEY  -> from https://console.groq.com/keys
"""

import os
import json
import random
import logging
import requests

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"  # free tier model on Groq


def _call_groq(messages, max_tokens=300, temperature=0.9):
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set — AI features disabled, using fallback.")
        return None

    try:
        resp = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.warning(f"Groq API call failed: {e}")
        return None


# ---------------------------------------------------------------------------
# 1. Deal caption generation — different style every time
# ---------------------------------------------------------------------------

CAPTION_STYLES = [
    "funny aur thoda masti wala",
    "urgent FOMO wala (limited time feel)",
    "premium aur classy tone",
    "casual dost jaisa tone",
    "excited emoji-heavy tone",
]


def ai_generate_caption(title, price, mrp, discount, affiliate_link):
    style = random.choice(CAPTION_STYLES)
    prompt = (
        f"Tum ek Indian e-commerce deals Instagram/Telegram page 'Trendora' ke liye "
        f"caption likhte ho. Hinglish mein likho (Hindi+English mix, jaisa Indian "
        f"social media par likha jata hai). Style: {style}.\n\n"
        f"Product: {title}\n"
        f"Price: ₹{int(price)}\n"
        f"MRP: ₹{int(mrp)}\n"
        f"Discount: {discount}%\n"
        f"Link: {affiliate_link}\n\n"
        f"Caption mein price, discount aur link zaroor include karo. "
        f"2-4 lines ka short caption do, kuch relevant emojis use karo, "
        f"end mein 3-4 hashtags do. Sirf caption text do, koi explanation nahi."
    )
    result = _call_groq([{"role": "user", "content": prompt}])
    if result:
        return result

    # Fallback: old static template
    return (
        f"🔥 {title}\n\n"
        f"💰 Price: ₹{int(price):,}  (MRP ₹{int(mrp):,})\n"
        f"🏷️ {discount}% OFF\n\n"
        f"👉 Grab it here: {affiliate_link}\n\n"
        f"#TrendoraDeals #DailyDeals #Shopping"
    )


# ---------------------------------------------------------------------------
# 2. Category auto-classification
# ---------------------------------------------------------------------------

VALID_CATEGORIES = ["mobile", "fashion", "electronics", "home", "beauty", "other"]


def ai_classify_category(title):
    prompt = (
        f"Product name: \"{title}\"\n\n"
        f"Isko in categories mein se ek mein classify karo: "
        f"{', '.join(VALID_CATEGORIES)}.\n"
        f"Sirf category ka naam likho, kuch aur nahi."
    )
    result = _call_groq([{"role": "user", "content": prompt}], max_tokens=10, temperature=0.2)
    if result:
        cleaned = result.strip().lower()
        for cat in VALID_CATEGORIES:
            if cat in cleaned:
                return cat
    return "other"  # fallback


# ---------------------------------------------------------------------------
# 3. Smart group reply — decides IF a reply is needed, then generates it
# ---------------------------------------------------------------------------

SMART_REPLY_SYSTEM = (
    "Tum 'Trendora' naam ke deals-Telegram-group ke helpful assistant ho. "
    "Group members deals, discounts, delivery, product genuineness jaise "
    "topics par sawal karte hain. Agar message ek genuine sawal hai jiska "
    "jawab dena chahiye, short Hinglish jawab do (max 2 lines). "
    "Agar message sirf casual chat hai, greeting hai, ya jawab ki zarurat "
    "nahi hai, to sirf 'NO_REPLY' likho — kuch aur nahi."
)


def ai_smart_reply(message_text):
    result = _call_groq(
        [
            {"role": "system", "content": SMART_REPLY_SYSTEM},
            {"role": "user", "content": message_text},
        ],
        max_tokens=120,
        temperature=0.6,
    )
    if not result:
        return None
    if "NO_REPLY" in result.upper():
        return None
    return result
