import logging

from database import
update_order_status

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import (
    ADMIN_BOT_TOKEN,
    ADMIN_ID,
)


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


# ================= ADMIN START =================

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if str(user_id) != str(ADMIN_ID):
        await update.message.reply_text(
            "❌ Access Denied"
        )
        return


    await update.message.reply_text(
        "⚙️ Admin Panel\n\n"
        "Welcome Admin!\n\n"
        "System is running."
    )


# ================= RUN BOT =================

app = Application.builder().token(ADMIN_BOT_TOKEN).build()

app.add_handler(
    CommandHandler(
        "start",
        admin_start
    )
)


print("Admin Bot Running...")

app.run_polling()
