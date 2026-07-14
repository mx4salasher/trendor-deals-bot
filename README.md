# Trendora Deal Bot — Setup Guide

Ye bot Telegram private chat mein tumse 2 links leta hai (original product link +
EarnKaro affiliate link), khud price/discount nikalta hai, ek branded deal-card
image banata hai, Telegram channel par auto-post karta hai, aur Instagram ke liye
image `instagram_ready/` folder mein save kar deta hai.

---

## Step 1 — Telegram Bot Token lena

1. Telegram par `@BotFather` ko message karo
2. `/newbot` bhejo, naam do (e.g. `TrendoraDealsBot`)
3. Jo token milega (kuch aisa: `123456:ABC-DEF...`) — save kar lo, ye `BOT_TOKEN` hai

## Step 1.5 — Apna Admin User ID nikalna

1. Telegram par `@userinfobot` ko message karo
2. Wo tumhara numeric user ID bhejega (e.g. `987654321`) — ye `ADMIN_USER_ID` hai
3. Ye zaroori hai kyunki sirf tum hi `/deal` aur `/broadcast` use kar paoge, group members nahi

## Step 1.6 — Free AI (Groq) setup — caption, category, smart-reply ke liye

1. [console.groq.com](https://console.groq.com) par sign up karo (sirf email se, credit card nahi chahiye)
2. **API Keys** section mein jaake naya key banao
3. Ye `GROQ_API_KEY` hai — env variable mein daal do
4. Free tier mein daily generous limit milta hai (deal-posting + group replies ke liye kaafi hai)
5. Agar `GROQ_API_KEY` set nahi karoge, bot AI features skip karke purana static-template wala behavior use kar lega — kabhi crash nahi hoga

## Step 2 — Channel ID nikalna

1. Apna Telegram channel banao (agar nahi bana)
2. Bot ko apne channel ka **admin** banao
3. Channel ka username hai to seedha `@yourchannelname` use kar sakte ho as `CHANNEL_ID`
4. Agar private channel hai (username nahi), to `@userinfobot` ko channel mein add karke
   numeric ID nikaal lo (kuch aisa dikhega: `-1001234567890`)

## Step 3 — Local test (optional, laptop par)

```bash
cd trendora_bot
pip install -r requirements.txt

# environment variables set karo (Mac/Linux):
export BOT_TOKEN="yaha_apna_token"
export CHANNEL_ID="@yourchannelname"
export ADMIN_USER_ID="yaha_apna_numeric_id"
export GROQ_API_KEY="yaha_apna_groq_key"

# Windows PowerShell:
# $env:BOT_TOKEN="yaha_apna_token"
# $env:CHANNEL_ID="@yourchannelname"
# $env:ADMIN_USER_ID="yaha_apna_numeric_id"
# $env:GROQ_API_KEY="yaha_apna_groq_key"

python bot.py
```

Telegram par apne bot ko private message karo: `/deal`

## Step 4 — Free 24/7 hosting (Railway) — laptop band rakh sakte ho

1. [railway.app](https://railway.app) par GitHub account se sign up karo (free tier available)
2. Ye poora `trendora_bot` folder ek GitHub repo mein push karo
3. Railway par **"New Project" → "Deploy from GitHub repo"** select karo
4. Railway khud `requirements.txt` dekh ke dependencies install kar lega
5. **Variables** tab mein jaake add karo:
   - `BOT_TOKEN` = apna token
   - `CHANNEL_ID` = apna channel ID
   - `ADMIN_USER_ID` = apna numeric user ID
   - `GROQ_API_KEY` = apna Groq key (AI features ke liye)
6. **Start command** set karo: `python bot.py`
7. Deploy hone ke baad bot 24/7 chalega — laptop band rakho, koi farak nahi padega

> Free tier har mahine limited hours deta hai — agar zyada use ho to Railway ka
> Hobby plan ($5/month) dekh sakte ho, ya Render.com ka free web-service tier
> try kar sakte ho (dono similar setup hai).

## Roz ka workflow (10 min)

1. Telegram par bot ko `/deal` bhejo
2. Original product link paste karo (Amazon/Flipkart)
3. Bot price/MRP khud nikal lega (fail hua to manually pooch lega)
4. EarnKaro affiliate link paste karo
5. Bot Telegram channel par auto-post karega
6. `instagram_ready/` folder khol ke wahi image + caption Instagram par upload kar do

## AI Features (naya)

| Feature | Kaise kaam karta hai |
|---|---|
| Auto caption | Har deal ka caption AI likhta hai — har baar alag style (funny, urgent, premium, casual) |
| Auto category | `/deal` flow mein ab AI khud category suggest karta hai, tum sirf "ok" bhejo ya galat ho to correct naam bhejo |
| Smart group reply | Members ke genuine sawalo ka natural jawab (sirf keyword-match nahi) — sirf question-jaise messages par trigger hota hai taaki free API limit bache |

Agar `GROQ_API_KEY` nahi set kiya, ya Groq ka free-tier limit khatam ho jaye kisi din,
bot khud purane static template/keyword-based behavior pe switch ho jata hai — kabhi
crash nahi hota, deal-posting kabhi rukta nahi.

## Group Admin Features (naya)

Bot ko apne **group** mein add karo aur ye admin rights do: **Delete Messages**
(spam removal ke liye). Channel mein sirf posting ke liye admin banao, delete
right zaroori nahi wahan.

| Feature | Kaise kaam karta hai |
|---|---|
| Welcome message | Naya member group join kare to bot khud welcome message bhejta hai |
| Spam/bad-word auto-delete | Non-whitelisted links ya banned words wale messages khud delete ho jate hain (edit `moderation.py` mein `BAD_WORDS` / `ALLOWED_DOMAINS` list) |
| FAQ auto-reply | "genuine hai?", "delivery kab?", "kaise kharide" jaise common questions ka auto-reply (`moderation.py` → `FAQ_KEYWORDS`) |
| Deal-request reply | Member "mobile deals chahiye" type kare to bot us category ke recent deals bhej deta hai |
| /broadcast (admin only, private chat) | `/broadcast Sale start ho gayi!` — sirf unhi users ko jaayega jinhone bot ko `/start` kiya ho private mein |

**Important:** Telegram members ko direct DM sirf tab jaa sakta hai jab wo pehle
bot ko private mein `/start` karein. Isliye channel/group description mein
likh do: "Deals updates ke liye bot ko /start karo: @yourbotusername"

`/deal` flow mein ab ek extra step hai — category select karna
(`mobile / fashion / electronics / home / beauty / other`), taaki deal-request
matching kaam kar sake.


- Amazon/Flipkart apna page-structure change karte rehte hain — agar scraping
  kabhi fail ho, bot khud manual entry maang lega, flow nahi rukega
- Har product ke liye pehle EarnKaro app mein ja ke affiliate link generate karo,
  phir bot ko do links do
- Instagram par auto-posting is version mein nahi hai (Instagram ki official API
  Business accounts ke liye complex approval maangti hai, aur unofficial automation
  se account ban ho sakta hai) — 10 min manual upload safest tareeka hai
