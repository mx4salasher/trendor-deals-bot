"""
bot.py
Trendora Telegram bot — deal posting + group admin features.

DEAL POSTING (private chat, admin only):
  /deal -> original link -> affiliate link -> category -> auto-posts to channel
           + saves Instagram-ready image

GROUP ADMIN FEATURES:
  - Welcomes new members
  - Auto-deletes spam links / banned words (bot needs "Delete Messages" admin right)
  - Auto-replies to common member questions (FAQ)
  - Detects "<category> deals chahiye" style requests and replies with recent deals
  - /broadcast (admin only, private chat) -> sends a message to every user who has
    ever /start'ed the bot in private chat (Telegram does not allow DMing users
    who haven't messaged the bot first — this is a platform rule, not a bot limit)

Environment variables required:
  BOT_TOKEN        -> from @BotFather
  CHANNEL_ID       -> e.g. @yourchannel or -1001234567890
  ADMIN_USER_ID    -> your own numeric Telegram user id (only you can post deals / broadcast)
"""

import os
import re
import logging
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from scraper import scrape_product
from image_generator import generate_deal_image
from moderation import is_spam, faq_reply, detect_category_request
import ai_client
import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID")

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instagram_ready")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Conversation states
(ASK_ORIGINAL_LINK, ASK_MANUAL_TITLE, ASK_MANUAL_PRICE, ASK_MANUAL_MRP,
 ASK_MANUAL_IMAGE, ASK_AFFILIATE_LINK, ASK_CATEGORY_CONFIRM) = range(7)


def is_url(text: str) -> bool:
    return bool(re.match(r"^https?://", text.strip()))


def is_admin(update: Update) -> bool:
    if not ADMIN_USER_ID:
        return True  # if not configured, don't lock anyone out during setup
    return str(update.effective_user.id) == str(ADMIN_USER_ID)


# ---------------------------------------------------------------------------
# Deal creation flow (private chat, admin only)
# ---------------------------------------------------------------------------

async def deal_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("Ye command sirf admin use kar sakta hai.")
        return ConversationHandler.END
    await update.message.reply_text(
        "Product ka ORIGINAL link bhejo (Amazon ya Flipkart wala, jisse price nikalna hai)."
    )
    return ASK_ORIGINAL_LINK


async def receive_original_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not is_url(url):
        await update.message.reply_text("Ye link valid nahi lag raha. Dobara bhejo.")
        return ASK_ORIGINAL_LINK

    context.user_data["original_link"] = url
    await update.message.reply_text("Price/title nikal raha hoon, thoda wait karo...")

    try:
        data = scrape_product(url)
        context.user_data["title"] = data["title"]
        context.user_data["price"] = data["price"]
        context.user_data["mrp"] = data["mrp"]
        context.user_data["image_url"] = data["image_url"]

        await update.message.reply_text(
            f"Mil gaya:\n"
            f"Product: {data['title']}\n"
            f"Price: ₹{data['price']}\n"
            f"MRP: ₹{data['mrp']}\n\n"
            f"Ab EarnKaro wala AFFILIATE link bhejo isi product ke liye."
        )
        return ASK_AFFILIATE_LINK

    except Exception as e:
        logger.warning(f"Scraping failed: {e}")
        await update.message.reply_text(
            "Auto-fetch fail ho gaya (website block kar sakti hai). "
            "Chalo manually karte hain. Product ka naam bhejo:"
        )
        return ASK_MANUAL_TITLE


async def receive_manual_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["title"] = update.message.text.strip()
    await update.message.reply_text("Current selling price bhejo (number only, e.g. 1999):")
    return ASK_MANUAL_PRICE


async def receive_manual_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["price"] = float(re.sub(r"[^\d.]", "", update.message.text))
    except ValueError:
        await update.message.reply_text("Sirf number bhejo, e.g. 1999")
        return ASK_MANUAL_PRICE
    await update.message.reply_text("MRP (original price) bhejo:")
    return ASK_MANUAL_MRP


async def receive_manual_mrp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["mrp"] = float(re.sub(r"[^\d.]", "", update.message.text))
    except ValueError:
        await update.message.reply_text("Sirf number bhejo, e.g. 2999")
        return ASK_MANUAL_MRP
    await update.message.reply_text("Product image ka direct link (URL) bhejo:")
    return ASK_MANUAL_IMAGE


async def receive_manual_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["image_url"] = update.message.text.strip()
    await update.message.reply_text("Ab EarnKaro wala AFFILIATE link bhejo isi product ke liye.")
    return ASK_AFFILIATE_LINK


async def receive_affiliate_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    affiliate_link = update.message.text.strip()
    if not is_url(affiliate_link):
        await update.message.reply_text("Ye link valid nahi lag raha. Dobara bhejo.")
        return ASK_AFFILIATE_LINK

    context.user_data["affiliate_link"] = affiliate_link

    await update.message.reply_text("Category detect kar raha hoon (AI)...")
    suggested = ai_client.ai_classify_category(context.user_data["title"])
    context.user_data["suggested_category"] = suggested

    await update.message.reply_text(
        f"AI ne category suggest ki hai: *{suggested}*\n"
        f"Sahi hai to 'ok' bhejo, warna correct naam bhejo "
        f"({', '.join(ai_client.VALID_CATEGORIES)})",
        parse_mode="Markdown",
    )
    return ASK_CATEGORY_CONFIRM


async def receive_category_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    if text in ("ok", "haan", "yes", "sahi", "sahi hai"):
        category = context.user_data["suggested_category"]
    elif text in ai_client.VALID_CATEGORIES:
        category = text
    else:
        await update.message.reply_text(
            f"'ok' bhejo ya inme se ek category naam bhejo: "
            f"{', '.join(ai_client.VALID_CATEGORIES)}"
        )
        return ASK_CATEGORY_CONFIRM

    ud = context.user_data
    affiliate_link = ud["affiliate_link"]
    price, mrp = ud["price"], ud["mrp"]
    discount = round((mrp - price) / mrp * 100) if mrp and mrp > price else 0

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(OUTPUT_DIR, f"deal_{timestamp}.jpg")

    await update.message.reply_text("Deal card aur AI caption banaraha hoon...")
    try:
        generate_deal_image(ud["title"], ud["image_url"], mrp, price, discount, image_path)
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        await update.message.reply_text(f"Image banane mein error aaya: {e}")
        return ConversationHandler.END

    caption = ai_client.ai_generate_caption(ud["title"], price, mrp, discount, affiliate_link)

    with open(image_path.replace(".jpg", "_caption.txt"), "w", encoding="utf-8") as f:
        f.write(caption)

    try:
        with open(image_path, "rb") as photo:
            await context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo, caption=caption)
        storage.add_deal(ud["title"], affiliate_link, category)
        await update.message.reply_text(
            "Telegram channel par post ho gaya ✅\n"
            f"Instagram ke liye image yahan save hai: {image_path}\n"
            "Bas usko Instagram par upload kar do."
        )
    except Exception as e:
        logger.error(f"Telegram post failed: {e}")
        await update.message.reply_text(
            f"Telegram par post nahi ho paya: {e}\n"
            f"Lekin image yahan ban gayi hai: {image_path}"
        )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancel kar diya.")
    return ConversationHandler.END


# ---------------------------------------------------------------------------
# /start — registers private-chat users so /broadcast can reach them later
# ---------------------------------------------------------------------------

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    storage.add_user(user.id, user.username or user.first_name or "")
    await update.message.reply_text(
        "Welcome to Trendora! 🎉 Ab tumhe naye deals ki updates milengi.\n"
        "(Admin ke liye: deal post karne ke liye /deal use karo)"
    )


# ---------------------------------------------------------------------------
# /broadcast — admin only, sends a message to all registered private users
# ---------------------------------------------------------------------------

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("Ye command sirf admin use kar sakta hai.")
        return

    message_text = " ".join(context.args)
    if not message_text:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    user_ids = storage.get_all_user_ids()
    sent, failed = 0, 0
    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=message_text)
            sent += 1
        except Exception:
            failed += 1

    await update.message.reply_text(f"Broadcast bheja: {sent} log tak pahunch gaya, {failed} fail hue.")


# ---------------------------------------------------------------------------
# Group handlers: welcome, moderation, FAQ auto-reply, deal-request
# ---------------------------------------------------------------------------

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        name = member.first_name or member.username or "dost"
        await update.message.reply_text(
            f"Welcome {name}! 👋 Trendora mein daily best deals milti hain. "
            "Koi bhi category ka deal chahiye ho to bas type karo, jaise: "
            "'mobile deals chahiye' 📱"
        )


async def moderate_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    if is_spam(message.text):
        try:
            await message.delete()
            logger.info(f"Deleted spam message from {message.from_user.id}")
        except Exception as e:
            logger.warning(f"Could not delete message (check bot admin rights): {e}")
        return  # don't also run FAQ/deal-request checks on deleted spam

    # Deal-request detection
    category = detect_category_request(message.text)
    if category:
        deals = storage.get_recent_deals_by_category(category)
        if deals:
            lines = [f"• {d['title']} — {d['link']}" for d in deals]
            await message.reply_text(
                f"Yeh {category} category ke latest deals hain:\n" + "\n".join(lines)
            )
        else:
            await message.reply_text(
                f"Abhi {category} category mein koi active deal nahi hai, jaldi aayegi 🙂"
            )
        return

    # FAQ auto-reply (fast keyword match first)
    reply = faq_reply(message.text)
    if reply:
        await message.reply_text(reply)
        return

    # AI smart reply — only triggered for question-like messages, to save free-tier usage
    looks_like_question = "?" in message.text or any(
        w in message.text.lower() for w in ["kya", "kaise", "kab", "kahan", "kyu", "kaun"]
    )
    if looks_like_question:
        ai_reply = ai_client.ai_smart_reply(message.text)
        if ai_reply:
            await message.reply_text(ai_reply)


def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        raise RuntimeError("BOT_TOKEN aur CHANNEL_ID environment variables set karo pehle.")

    app = Application.builder().token(BOT_TOKEN).build()

    # Deal creation conversation — private chat only
    conv = ConversationHandler(
        entry_points=[CommandHandler("deal", deal_start, filters=filters.ChatType.PRIVATE)],
        states={
            ASK_ORIGINAL_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_original_link)],
            ASK_MANUAL_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_manual_title)],
            ASK_MANUAL_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_manual_price)],
            ASK_MANUAL_MRP: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_manual_mrp)],
            ASK_MANUAL_IMAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_manual_image)],
            ASK_AFFILIATE_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_affiliate_link)],
            ASK_CATEGORY_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_category_confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("start", start_command, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("broadcast", broadcast_command, filters=filters.ChatType.PRIVATE))

    # Group-only handlers
    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS & filters.ChatType.GROUPS, welcome_new_member
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS, moderate_group_message
    ))

    logger.info("Trendora bot chal raha hai...")
    app.run_polling()


if __name__ == "__main__":
    main()
