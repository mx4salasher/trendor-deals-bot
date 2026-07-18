import os
import logging
from datetime import datetime

from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    ContextTypes,
    filters
)

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from deal_finder import get_best_deal
from earnkaro_client import get_affiliate_link
from storage import is_posted, mark_posted, get_stats
from ai_client import get_ai_reply


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

POST_INTERVAL = 1200


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)



async def send_deal(context: ContextTypes.DEFAULT_TYPE):

    try:

        deal = await get_best_deal()


        if not deal:
            logger.info("No deal found")
            return


        if is_posted(deal["link"]):
            logger.info("Already posted")
            return



        affiliate_url = await get_affiliate_link(
            deal["link"]
        )


        if (
            not affiliate_url
            or not affiliate_url.startswith("http")
        ):

            logger.error(
                f"Invalid affiliate URL: {affiliate_url}"
            )

            return



        track_url = (
            affiliate_url
            + "?utm_source=tg_bot"
        )



        caption = (
            f"🔥 *{deal['store']} - {deal['title']}*\n\n"
            f"💰 Price: ₹{deal['price']}\n"
            f"🏷️ Discount: {deal['discount']}\n"
            f"⭐ Rating: {deal['rating']}\n\n"
            f"👉 *Buy Now*\n"
            f"{track_url}\n\n"
            f"#Deals #{deal['category'].split(',')[0]}"
        )


        keyboard = [

            [

                InlineKeyboardButton(
                    f"🛒 Buy from {deal['store']}",
                    url=track_url
                )

            ]

        ]


        await context.bot.send_photo(

            chat_id=CHANNEL_ID,

            photo=deal["image"],

            caption=caption,

            parse_mode="Markdown",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )

        )


        mark_posted(
            deal["link"]
        )


        logger.info(
            f"Posted: {deal['title']} from {deal['store']}"
        )


    except Exception as e:

        logger.error(
            f"Error in send_deal: {e}"
        )




async def welcome_new_member(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.chat_member:

        member = update.chat_member.new_chat_member.user


        await context.bot.send_message(

            chat_id=update.chat_member.chat.id,

            text=(
                f"Hey {member.first_name}! 👋\n"
                "Welcome to Deals Loot 🔥"
            )

        )





async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return


    user_msg = update.message.text


    reply = await get_ai_reply(
        user_msg
    )


    await update.message.reply_text(
        reply
    )





async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "Bot Live hai ✅\n\n"
        "/stats - Report\n"
        "/postnow - Force Deal"
    )





async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return


    data = get_stats()


    await update.message.reply_text(

        f"📊 Report\n\n"
        f"Deals: {data['posted']}\n"
        f"Clicks: {data['clicks']}\n"
        f"Earning: ₹{data['earning']}"

    )





async def post_now(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != ADMIN_ID:
        return


    await update.message.reply_text(
        "Posting deal..."
    )


    await send_deal(
        context
    )


    await update.message.reply_text(
        "Done ✅"
    )





async def daily_report(
    context: ContextTypes.DEFAULT_TYPE
):

    data = get_stats()


    await context.bot.send_message(

        chat_id=ADMIN_ID,

        text=(
            f"📈 Daily Report\n\n"
            f"Date: {datetime.now().strftime('%d-%m-%Y')}\n"
            f"Deals: {data['posted']}\n"
            f"Clicks: {data['clicks']}\n"
            f"Earning: ₹{data['earning']}"
        )

    )





def main():

    app = Application.builder().token(
        BOT_TOKEN
    ).build()


    app.add_handler(
        CommandHandler("start", start)
    )


    app.add_handler(
        CommandHandler("stats", stats)
    )


    app.add_handler(
        CommandHandler("postnow", post_now)
    )


    app.add_handler(
        ChatMemberHandler(
            welcome_new_member,
            ChatMemberHandler.CHAT_MEMBER
        )
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )



    scheduler = AsyncIOScheduler()


    scheduler.add_job(
        send_deal,
        "interval",
        seconds=POST_INTERVAL,
        args=[app]
    )


    scheduler.add_job(
        daily_report,
        "cron",
        hour=21,
        minute=0,
        args=[app]
    )


    scheduler.start()



    logger.info(
        "Bot Started. Full Auto Mode ON"
    )


    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )



if __name__ == "__main__":
    main()