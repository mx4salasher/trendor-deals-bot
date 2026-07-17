import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from deal_finder import get_best_deal
from earnkaro_client import get_affiliate_link
from storage import is_posted, mark_posted

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_deal_to_channel(context: ContextTypes.DEFAULT_TYPE):
    deal = await get_best_deal()
    if not deal:
        logger.info("No new deal found")
        return
    
    if is_posted(deal['link']):
        logger.info("Deal already posted")
        return

    affiliate_url = await get_affiliate_link(deal['link'])
    
    caption = f"🔥 *{deal['title']}*\n\n💰 Price: ₹{deal['price']}\n🏷️ Discount: {deal['discount']}\n\n👉 {affiliate_url}\n\n#Deal #Offer"
    
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=deal['image'], caption=caption, parse_mode='Markdown')
    mark_posted(deal['link'])
    logger.info(f"Posted: {deal['title']}")

async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Running auto post job...")
    await send_deal_to_channel(context)

async def force_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("Force posting a deal...")
    await send_deal_to_channel(context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is Live! I will post deals every 20 minutes.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("forcepost", force_post))
    
    # Scheduler for auto post every 20 min = 1200 sec
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: asyncio.run(auto_post(app)), 'interval', seconds=1200, id='auto_post')
    scheduler.start()
    
    logger.info("Bot Started. Auto-post every 20 minutes")
    app.run_polling()

if __name__ == '__main__':
    main()