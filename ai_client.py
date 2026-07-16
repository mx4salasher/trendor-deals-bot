"""
ai_client.py
Handles Groq API integration for Category Classification, 
Deal Caption Generation, and AI Smart Replies.
"""
import os
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

VALID_CATEGORIES = [
    "electronics", "fashion", "home & kitchen", "beauty & personal care", 
    "fitness", "grocery", "toys & baby care", "books & stationery"
]

def get_client():
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY setting miss ho gaya hai check environment.")
    return Groq(api_key=GROQ_API_KEY)

def ai_classify_category(title: str) -> str:
    try:
        client = get_client()
        prompt = (
            f"Classify this product into exactly one of these categories: {', '.join(VALID_CATEGORIES)}.\n"
            f"Product: '{title}'\n"
            f"Return only the category name in lowercase. No extra words or punctuation."
        )
        completion = client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=10
        )
        result = completion.choices[0].message.content.strip().lower()
        if result in VALID_CATEGORIES:
            return result
        return "electronics"  # Default fallback
    except Exception:
        return "electronics"

def ai_generate_caption(title: str, price: float, mrp: float, discount: int, affiliate_link: str) -> str:
    try:
        client = get_client()
        prompt = (
            f"Create an engaging Telegram deal channel caption in Hinglish (Hindi written in English) for this product:\n"
            f"Product: {title}\n"
            f"Price: Rs. {price}\n"
            f"MRP: Rs. {mrp}\n"
            f"Discount: {discount}%\n"
            f"Affiliate link: {affiliate_link}\n\n"
            f"Guidelines:\n"
            f"- Use high-converting emojis (e.g., 🔥, 🚨, 💥).\n"
            f"- Keep it precise, bold key points, and emphasize the deal discount.\n"
            f"- Make sure the final output has a call-to-action with the affiliate link.\n"
            f"Return ONLY the caption text. No chat intro/outro."
        )
        completion = client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=250
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        # Solid markdown fallback caption if API fails
        return (
            f"🔥 *LOOT DEAL!* 🔥\n\n"
            f"📌 *{title}*\n"
            f"💰 *Deal Price:* ₹{price} \n"
            f"❌ *MRP:* ~₹{mrp}~\n"
            f"📉 *Save:* {discount}% Instant Discount!\n\n"
            f"🛒 *Loot Lo:* {affiliate_link}"
        )

def ai_smart_reply(user_message: str) -> str:
    try:
        client = get_client()
        prompt = (
            f"You are Trendora Support AI. Answer this query naturally in one or two short sentences "
            f"using Hinglish. Be extremely helpful but concise:\n"
            f"User Question: '{user_message}'\n"
            f"Response:"
        )
        completion = client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=60
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        return ""