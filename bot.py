import os
import asyncio
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ChatMemberHandler, ContextTypes, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from deal_finder import get_best_deal
from earnkaro_client import get_affiliate_link
from storage import is_posted, mark_posted, get_stats, add_click
from ai_client import get_ai_reply

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
POST_INTERVAL = 1200 # 20 min

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_deal(context: ContextTypes.DEFAULT_TYPE):
    try:
        deal = await get_best_deal()
        if not deal: return
        if is_posted(deal['link']): return

        affiliate_url = await get_affiliate_link(deal['link'])
        track_url = f"{affiliate_url}?utm_source=tg_bot"

        caption = f"🔥 *{deal['store']} - {deal['title']}*\n\n💰 Price: ₹{deal['price']}\n🏷️ Discount: {deal['discount']}\n⭐ Rating: {deal['rating']}\n\n👉 *Buy Now*: {track_url}\n\n#Deals #Loot #{deal['category'].split(',')[0]}"

        keyboard = [[InlineKeyboardButton(f"🛒 Buy from {deal['store']}", url=track_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_photo(chat_id=CHANNEL_ID, photo=deal['image'], caption=caption, parse_mode='Markdown', reply_markup=reply_markup)
        mark_posted(deal['link'])
        logger.info(f"Posted: {deal['title']} from {deal['store']}")
    except Exception as e:
        logger.error(f"Error in send_deal: {e}")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.chat_member and update.chat_member.new_chat_members:
        for member in update.chat_member.new_chat_members:
            welcome = f"Hey {member.first_name}! 👋\nWelcome to *Deals Loot* 🔥\n\nMai har 20 min me *EarnKaro* ki best deals lata hu. Koi sawal ho to yahi puch lo, mai AI Admin hu 😎"
            await context.bot.send_message(chat_id=update.chat_member.chat.id, text=welcome, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    if str(update.message.chat.id)!= CHANNEL_ID: return

    user_msg = update.message.text
    ai_reply = await get_ai_reply(user_msg)
    await update.message.reply_text(ai_reply, parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Live hai ✅\n\nCommands:\n/stats - Aaj ki earning\n/postnow - Force deal post")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID: return
    data = get_stats()
    text = f"📊 *Aaj ki Report*\n\nDeals Posted: {data['posted']}\nTotal Clicks: {data['clicks']}\nEst. Earning: ₹{data['earning']}\n\nBot 24x7 kaam kar raha hai 💰"
    await update.message.reply_text(text, parse_mode='Markdown')

async def post_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID: return
    await update.message.reply_text("Force posting 1 deal...")
    await send_deal(context)
    await update.message.reply_text("Posted ✅")

async def daily_report(context: ContextTypes.DEFAULT_TYPE):
    data = get_stats()
    text = f"📈 *Daily Report - {datetime.now().strftime('%d-%m-%Y')}*\n\nDeals: {data['posted']}\nClicks: {data['clicks']}\nEarning: ₹{data['earning']}\n\nSona bhai, bot sambhal lega 😎"
    await context.bot.send_message(chat_id=ADMIN_ID, text=text, parse_mode='Markdown')

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("postnow", post_now))
    app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_deal, 'interval', seconds=POST_INTERVAL, args=[app])
    scheduler.add_job(daily_report, 'cron', hour=21, minute=0, args=[app])
    scheduler.start()

    logger.info("Bot Started. Full Auto Mode ON with 22 EarnKaro Stores")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()