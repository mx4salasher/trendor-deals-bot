import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from deal_finder import find_deals
from earnkaro_client import get_affiliate_link
from ai_client import generate_caption
import storage

# Variables Railway se
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = os.getenv("ADMIN_ID")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def auto_post(app):
    """Har 20 min me deal dhunde aur post kare"""
    try:
        logger.info("Checking for new deals...")
        deals = await find_deals()
        
        for deal in deals:
            if storage.is_new_deal(deal['url']):
                # Earnkaro link banao
                aff_link = get_affiliate_link(deal['url'])
                
                # Groq se caption banwao
                caption = await generate_caption(deal, aff_link)
                
                # Telegram Channel pe post
                await app.bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=deal['image'],
                    caption=caption,
                    parse_mode="HTML"
                )
                storage.mark_posted(deal['url'])
                logger.info(f"Posted: {deal['title']}")
                await asyncio.sleep(3) # spam na ho
                
    except Exception as e:
        logger.error(f"Error in auto_post: {e}")

async def forcepost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual test ke liye /forcepost command"""
    if str(update.effective_user.id)!= ADMIN_ID:
        return
    await update.message.reply_text("Force posting started...")
    await auto_post(context.application)
    await update.message.reply_text("Done! Check channel.")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("forcepost", forcepost))

    # Scheduler - har 20 min
    scheduler = AsyncIOScheduler()
    scheduler.add_job(auto_post, 'interval', minutes=20, args=[app])
    scheduler.start()
    
    logger.info("Bot Started. Auto-post every 20 minutes")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())