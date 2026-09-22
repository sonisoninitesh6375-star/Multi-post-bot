import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

# Channels where the bot is admin
CHANNELS = set()

# Only the first person who uses /start becomes the owner
OWNER_ID = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global OWNER_ID

    user_id = update.effective_user.id

    if OWNER_ID is None:
        OWNER_ID = user_id
        await update.message.reply_text(
            "✅ Bot activated!\n\n"
            "अब मुझे कोई भी पोस्ट भेजो और वह connected channels में जाएगी."
        )
    elif user_id == OWNER_ID:
        await update.message.reply_text("✅ Bot is ready.")
    else:
        await update.message.reply_text("❌ Access denied.")


async def detect_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post:
        CHANNELS.add(update.channel_post.chat.id)
        print("Channel detected:", update.channel_post.chat.id)


async def send_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if OWNER_ID != update.effective_user.id:
        return

    if not CHANNELS:
        await update.message.reply_text(
            "❌ अभी कोई channel detect नहीं हुआ.\n\n"
            "दोनों channels में एक-एक test post डालो."
        )
        return

    success = 0

    for channel_id in CHANNELS:
        try:
            await context.bot.copy_message(
                chat_id=channel_id,
                from_chat_id=update.effective_chat.id,
                message_id=update.message.message_id,
            )
            success += 1
        except Exception as e:
            print("Error:", e)

    await update.message.reply_text(
        f"✅ Post sent to {success}/{len(CHANNELS)} channels."
    )


async def show_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if OWNER_ID != update.effective_user.id:
        return

    if CHANNELS:
        text = "📢 Connected Channels:\n\n"
        text += "\n".join(str(x) for x in CHANNELS)
    else:
        text = "❌ No channels detected."

    await update.message.reply_text(text)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("channels", show_channels))

    # Detect messages posted inside channels
    app.add_handler(
        MessageHandler(
            filters.UpdateType.CHANNEL_POST,
            detect_channel
        )
    )

    # Receive normal messages sent to the bot
    app.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            send_post
        )
    )

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
