import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

# Users allowed to use the bot
AUTHORIZED_USERS = {
    8743303707,
    5987711918,
}

# Connected private channels
CHANNELS = {
    -1003823185479,
    -1004326580585,
}


def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Access denied.")
        return

    await update.message.reply_text(
        "✅ Bot ready!\n\n"
        "Text, photo, video or document भेजो — "
        "दोनों connected channels में चला जाएगा."
    )


async def show_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    text = "📢 Connected Channels:\n\n"
    text += "\n".join(str(channel) for channel in CHANNELS)

    await update.message.reply_text(text)


async def send_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("❌ Access denied.")
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
            print(f"Error sending to {channel_id}: {e}")

    await update.message.reply_text(
        f"✅ Post sent to {success}/{len(CHANNELS)} channels."
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("channels", show_channels))

    app.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            send_post
        )
    )

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
