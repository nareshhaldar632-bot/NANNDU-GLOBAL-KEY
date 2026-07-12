import logging
import uuid

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN, ADMIN_ID, UPI_ID, QR_IMAGE
from products import PRODUCTS, DURATIONS
from database import create_tables, add_user, add_order


logging.basicConfig(level=logging.INFO)


user_orders = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    add_user(
        user.id,
        user.username,
        user.first_name
    )

    keyboard = [
        [InlineKeyboardButton("🛒 Products", callback_data="products")],
        [InlineKeyboardButton("Contact Admin", url="https://t.me/your_username")]
    ]

    await update.message.reply_text(
        "Welcome to Store Bot\n\nSelect an option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "products":

        buttons = []

        for p in PRODUCTS:
            buttons.append([
                InlineKeyboardButton(
                    p["name"],
                    callback_data=f"product_{p['id']}"
                )
            ])

        await query.edit_message_text(
            "Select Product:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


    elif query.data.startswith("product_"):

        product_id = query.data.replace("product_", "")

        buttons = []

        for d in DURATIONS:
            buttons.append([
                InlineKeyboardButton(
                    f"{d} ₹{DURATIONS[d]}",
                    callback_data=f"buy_{product_id}_{d}"
                )
            ])

        await query.edit_message_text(
            "Select Duration:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


    elif query.data.startswith("buy_"):

        data = query.data.split("_")

        product_id = data[1]
        duration = data[2]

        product_name = next(
            p["name"] for p in PRODUCTS
            if p["id"] == product_id
        )

        amount = DURATIONS[duration]

        order_id = str(uuid.uuid4())[:8]

        user_orders[query.from_user.id] = {
            "order_id": order_id,
            "product": product_name,
            "duration": duration,
            "amount": amount
        }

        await query.edit_message_text(
            f"Order ID: {order_id}\n\n"
            f"Product: {product_name}\n"
            f"Duration: {duration}\n"
            f"Amount: ₹{amount}\n\n"
            f"UPI: {UPI_ID}\n\n"
            "Payment ke baad UTR number bheje."
        )

        await context.bot.send_photo(
            chat_id=query.from_user.id,
            photo=QR_IMAGE
        )


async def utr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in user_orders:
        return

    utr = update.message.text

    order = user_orders[user_id]

    add_order(
        order["order_id"],
        user_id,
        order["product"],
        order["duration"],
        order["amount"],
        utr
    )


    await context.bot.send_message(
        ADMIN_ID,
        f"New Order\n\n"
        f"ID: {order['order_id']}\n"
        f"Product: {order['product']}\n"
        f"Duration: {order['duration']}\n"
        f"Amount: ₹{order['amount']}\n"
        f"UTR: {utr}"
    )

    await update.message.reply_text(
        "✅ UTR received. Admin approval ka wait karein."
    )


def main():

    create_tables()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(
        MessageHandler(filters.TEXT, utr_handler)
    )

    app.run_polling()


if __name__ == "__main__":
    main()
