import os, random
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

STYLES = ["hype", "urgent", "minimal", "funny"]

async def generate_caption(product):
    style = random.choice(STYLES)
    tags = f"#{product['store']} #deals #sale #trendora"

    prompt = f"""Write a {style} Telegram caption for this deal:
Product: {product['title']}
Price: {product['price']}
MRP: {product['mrp']}
Discount: {product['discount']}% OFF
Link: {product['affiliate_link']}

Format:
🔥 Emoji + Product Name
💰 Price + Discount
✅ Key point
🛒 Buy Now + Link
{tags}
Keep it under 400 characters. No extra text."""

    try:
        res = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.8
        )
        return res.choices[0].message.content
    except Exception as e:
        print(f"[AI ERROR] {e}")
        # Fallback agar AI fail ho jaye
        return f"""🔥 {product['title']}
💰 Deal Price: {product['price']}
❌ MRP: {product['mrp']}
✅ {product['discount']}% OFF

🛒 Buy Now 👇
{product['affiliate_link']}

{tags}"""