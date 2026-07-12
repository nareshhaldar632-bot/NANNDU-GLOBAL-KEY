import uuid
import logging

from database import add_order

from config import ADMIN_BOT_TOKEN, ADMIN_ID

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import (
    BOT_TOKEN,
    CHANNEL_URL,
    UPI_ID,
    QR_IMAGE,
)

from database import (
    create_tables,
    add_user,
)

from products import (
    PRODUCTS,
    DURATIONS,
)

# ----------------------------

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

create_tables()

# ----------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    add_user(
        user.id,
        user.username,
        user.first_name,
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🛒 Products",
                callback_data="products"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 Join Channel",
                url=CHANNEL_URL
            )
        ]
    ]

    await update.message.reply_text(
        f"""👋 Welcome {user.first_name}

🛍️ Welcome to Nandu Global Key Store

Please choose an option below.""",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# ================= PRODUCTS MENU =================

async def products_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = []

    for product in PRODUCTS:
        keyboard.append([
            InlineKeyboardButton(
                product,
                callback_data=f"product|{product}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("⬅ Back", callback_data="home")
    ])

    await query.edit_message_text(
        "🛒 Select Product",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def product_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product = query.data.split("|")[1]

    context.user_data["product"] = product

    keyboard = []

    for duration, price in DURATIONS.items():

        keyboard.append([
            InlineKeyboardButton(
                f"{duration} - ₹{price}",
                callback_data=f"duration|{duration}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅ Back",
            callback_data="products"
        )
    ])

    await query.edit_message_text(
        f"📦 Product : {product}\n\n"
        "⏳ Select Duration",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def duration_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    duration = query.data.split("|")[1]

    product = context.user_data.get("product")

    if product is None:
        await query.edit_message_text(
            "❌ Session Expired\n\nPlease use /start again."
        )
        return

    amount = DURATIONS[duration]

    order_id = str(uuid.uuid4())[:8].upper()

    context.user_data["order_id"] = order_id
    context.user_data["duration"] = duration
    context.user_data["amount"] = amount

    with open(QR_IMAGE, "rb") as photo:

        await query.message.reply_photo(
            photo=photo,
            caption=(
                f"🆔 Order ID : {order_id}\n\n"
                f"📦 Product : {product}\n"
                f"⏳ Duration : {duration}\n"
                f"💰 Amount : ₹{amount}\n\n"
                f"💳 UPI ID : {UPI_ID}\n\n"
                "✅ Payment karne ke baad apna UTR Number send karein."
            )
        )

    await query.message.reply_text(
        "✍️ Please send your UTR Number."
    )

# ================= UTR RECEIVE =================

async def receive_utr(update: Update, context: ContextTypes.DEFAULT_TYPE):

    utr = update.message.text

    product = context.user_data.get("product")
    duration = context.user_data.get("duration")
    amount = context.user_data.get("amount")
    order_id = context.user_data.get("order_id")

    if not order_id:
        await update.message.reply_text(
            "❌ Order nahi mila.\nPlease /start se dobara karein."
        )
        return


    add_order(
        order_id,
        update.effective_user.id,
        product,
        duration,
        amount,
        utr
    )

    admin_bot = Bot(token=ADMIN_BOT_TOKEN)

    await admin_bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "🆕 New Order Received\n\n"
            f"🆔 Order ID: {order_id}\n"
            f"👤 User ID: {update.effective_user.id}\n"
            f"📦 Product: {product}\n"
            f"⏳ Duration: {duration}\n"
            f"💰 Amount: ₹{amount}\n"
            f"💳 UTR: {utr}\n\n"
            "Please check and approve/reject."
        )
    )

    await update.message.reply_text(
        "✅ UTR Received\n\n"
        "⏳ Aapka order admin verification mein hai."
    )

    admin_bot = Bot(token=ADMIN_BOT_TOKEN)

    await admin_bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "🆕 New Order Received\n\n"
            f"🆔 Order ID: {order_id}\n"
            f"👤 User ID: {update.effective_user.id}\n"
            f"📦 Product: {product}\n"
            f"⏳ Duration: {duration}\n"
            f"💰 Amount: ₹{amount}\n"
            f"💳 UTR: {utr}\n\n"
            "Please check and approve/reject."
        )
    )

application = Application.builder().token(BOT_TOKEN).build()

application.add_handler(CallbackQueryHandler(products_menu, pattern="^products$"))
application.add_handler(CallbackQueryHandler(product_selected, pattern="^product\\|"))
application.add_handler(CallbackQueryHandler(duration_selected, pattern="^duration\\|"))

application.run_polling()
