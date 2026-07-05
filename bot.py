import psutil
import socket
import random
import string
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, ADMIN_ID
import db


# =====================
# STATES CREATE FLOW
# =====================
USERNAME, PASSWORD, DAYS = range(3)


# =====================
# SYSTEM INFO
# =====================
def get_ip():
    return socket.gethostbyname(socket.gethostname())

def gen_pass(length=6):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


# =====================
# MENU PRINCIPAL
# =====================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 STATUS", callback_data="status")],
        [InlineKeyboardButton("👤 USERS", callback_data="users")],
        [InlineKeyboardButton("➕ CREATE USER", callback_data="create")],
        [InlineKeyboardButton("🗑 DELETE USER", callback_data="delete")],
        [InlineKeyboardButton("📡 ACTIVE", callback_data="active")],
        [InlineKeyboardButton("🔄 REFRESH", callback_data="refresh")],
    ])


# =====================
# START
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 SAAS HOSTING PANEL ONLINE",
        reply_markup=main_menu()
    )


# =====================
# CALLBACKS PRINCIPALES
# =====================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    await q.answer()

    # STATUS
    if data == "status":
        await q.edit_message_text(
            f"""🖥 VPS STATUS

🌐 IP: {get_ip()}
⚙️ CPU: {psutil.cpu_percent()}%
🧠 RAM: {psutil.virtual_memory().percent}%""",
            reply_markup=main_menu()
        )

    # USERS
    elif data == "users":
        rows = db.get_users()

        msg = "👤 USERS\n\n"
        for u in rows:
            msg += f"{u[0]} | {u[1]} | {u[2]}\n"

        await q.edit_message_text(msg, reply_markup=main_menu())

    # CREATE FLOW START
    elif data == "create":
        await q.edit_message_text("👤 Envía USERNAME:")
        return USERNAME

    # DELETE MENU
    elif data == "delete":
        rows = db.get_users()

        keyboard = [
            [InlineKeyboardButton(f"❌ {u[0]}", callback_data=f"del_{u[0]}")]
            for u in rows
        ]

        keyboard.append([InlineKeyboardButton("⬅ BACK", callback_data="back")])

        await q.edit_message_text(
            "🗑 SELECT USER TO DELETE:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # DELETE ACTION
    elif data.startswith("del_"):
        user = data.replace("del_", "")
        db.delete_user(user)

        await q.edit_message_text("🗑 USER DELETED", reply_markup=main_menu())

    # ACTIVE USERS
    elif data == "active":
        rows = db.get_users()
        now = datetime.now()

        active = 0
        for u in rows:
            try:
                if datetime.fromisoformat(u[2]) > now:
                    active += 1
            except:
                pass

        await q.edit_message_text(f"📡 ACTIVE USERS: {active}", reply_markup=main_menu())

    # REFRESH
    elif data == "refresh":
        await q.edit_message_text("🔄 UPDATED", reply_markup=main_menu())

    # BACK
    elif data == "back":
        await q.edit_message_text("🏠 MAIN MENU", reply_markup=main_menu())


# =====================
# CREATE FLOW (FIX REAL)
# =====================
async def create_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["username"] = update.message.text

    await update.message.reply_text("🔑 PASSWORD (o escribe AUTO):")
    return PASSWORD


async def create_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pwd = update.message.text

    if pwd.lower() == "auto":
        pwd = gen_pass()

    context.user_data["password"] = pwd

    await update.message.reply_text("⏳ DIAS DE EXPIRACIÓN:")
    return DAYS


async def create_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        days = int(update.message.text)

        user = context.user_data["username"]
        password = context.user_data["password"]

        expiry = (datetime.now() + timedelta(days=days)).isoformat()

        db.create_user(user, password, expiry)

        await update.message.reply_text(
            f"""✅ USER CREATED

👤 USER: {user}
🔑 PASS: {password}
⏳ EXP: {days} days
🌐 VPS IP: {get_ip()}"""
        )

        return ConversationHandler.END

    except:
        await update.message.reply_text("❌ INVALID NUMBER")
        return DAYS


# =====================
# CANCEL
# =====================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ CANCELLED")
    return ConversationHandler.END


# =====================
# BUILD BOT (FIX FINAL)
# =====================
def build_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # CALLBACKS
    app.add_handler(CallbackQueryHandler(buttons))

    # CREATE FLOW CORRECTO
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(buttons, pattern="^create$")],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_password)],
            DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_days)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)

    # START
    app.add_handler(CommandHandler("start", start))

    return app