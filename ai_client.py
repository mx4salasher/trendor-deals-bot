import os
from groq import Groq
import asyncio

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def generate_caption(deal, affiliate_link):
    """Groq se deal ke liye catchy caption banwata hai"""
    
    title = deal['title']
    price = deal['price']
    original_price = deal.get('original_price', '')
    discount = deal.get('discount', '')
    
    prompt = f"""
    You are a deal hunter for Telegram. Write a short, catchy, Hinglish caption for this product deal.
    Use emojis. Make it exciting and urgent. Add hashtags.
    
    Product: {title}
    Price: {price}
    MRP: {original_price}
    Discount: {discount}
    Link: {affiliate_link}
    
    Format:
    🔥 DEAL ALERT 🔥
    [Product Name]
    💰 Price: [Price] ~~[MRP]~~ ([Discount] OFF)
    
    [1 line catchy reason to buy]
    
    👉 Buy Now: [Link]
    
    #Deal #Offer #Trending
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192", # Groq ka fast model
            temperature=0.7,
            max_tokens=300,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Groq Error: {e}")
        # Agar Groq fail ho to default caption
        return f"""🔥 DEAL ALERT 🔥
{title}
💰 Price: {price} ~~{original_price}~~ ({discount} OFF)

👉 Buy Now: {affiliate_link}

#Deal #Offer"""