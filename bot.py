import os, asyncio, logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from deal_finder import find_deals
from earnkaro_client import get_affiliate_link
from ai_client import generate_caption
import storage

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")
ADMIN = os.getenv("ADMIN_ID")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

async def auto_post(app):
    try:
        logging.info("Checking for new deals...")
        deals = await find_deals()
        if not deals:
            logging.info("No new deals found")
            return

        d = deals[0]
        d["affiliate_link"] = await get_affiliate_link(d["product_url"])
        d["caption"] = await generate_caption(d)

        await app.bot.send_photo(CHANNEL, d["image_url"], caption=d["caption"])
        storage.add_deal(d)
        await app.bot.send_message(ADMIN, f"✅ Posted: {d['title'][:50]}...")
        logging.info(f"Posted deal: {d['title'][:50]}")

    except Exception as e:
        logging.error(f"POST ERR: {e}")
        await app.bot.send_message(ADMIN, f"❌ Error: {e}")

async def start(u, c):
    await u.message.reply_text("Trendora Deals V2.0 Live 🔥\nAuto posting every 20 min")

async def health(u, c):
    await u.message.reply_text("Bot Healthy ✅\nScheduler Running")

async def stats(u, c):
    s = storage.get_stats()
    await u.message.reply_text(f"📊 Total Deals Posted: {s['total_posted']}")

async def forcepost(u, c):
    await u.message.reply_text("Finding deal...")
    await auto_post(c.application)
    await u.message.reply_text("Done ✅")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CommandHandler("admin", stats))
    app.add_handler(CommandHandler("forcepost", forcepost))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(auto_post(app)), 'interval', minutes=20)
    scheduler.start()

    logging.info("Bot Started. Auto-post every 20 minutes")
    app.run_polling()

if __name__ == "__main__":
    main()