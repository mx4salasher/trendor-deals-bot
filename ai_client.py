from groq import Groq
import os
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def get_ai_reply(user_msg):
    try:
        res = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Tu 'Deals Loot' telegram channel ka AI Admin hai. Hindi me, dosti se, 2-3 line me reply de. Product puchne par help kar."},
                {"role": "user", "content": user_msg}
            ], model="llama-3.1-8b-instant", max_tokens=200)
        return res.choices[0].message.content
    except: return "Bhai 2 min ruk, server busy hai 😅"