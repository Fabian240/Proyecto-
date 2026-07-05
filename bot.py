import psutil
import socket
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from config import BOT_TOKEN, ADMIN_ID
import db


# =====================
# SYSTEM INFO
# =====================
def get_ip():
    return socket.gethostbyname(socket.gethostname())

def get_cpu():
    return psutil.cpu_percent(interval=1)

def get_ram():
    return psutil.virtual_memory().percent

def get_disk():
    return psutil.disk_usage('/').percent


# =====================
# START
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 STATUS", callback_data="status")],
        [InlineKeyboardButton("👤 USERS", callback_data="users")],
        [InlineKeyboardButton("📋 CMD", callback_data="cmds")],
    ]

    await update.message.reply_text(
        "🚀 CHOMELO SaaS ONLINE",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =====================
# CREATE USER
# =====================
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ No autorizado")

    try:
        user = context.args[0]
        password = context.args[1]
        expire_days = int(context.args[2])

        expire = (datetime.now() + timedelta(days=expire_days)).isoformat()

        db.create_user(user, password, expire)

        await update.message.reply_text(
            f"✅ USER CREADO\n\n👤 {user}\n📅 Expira en: {expire_days} días"
        )

    except:
        await update.message.reply_text("❌ Uso: /create user pass dias")


# =====================
# LIST USERS
# =====================
async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ No autorizado")

    rows = db.get_users()

    msg = "👤 USERS:\n\n"
    for u in rows:
        msg += f"{u[0]} | {u[1]} | {u[2]}\n"

    await update.message.reply_text(msg)


# =====================
# STATUS VPS
# =====================
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"""
🖥 CHOMELO VPS STATUS

🌐 IP: {get_ip()}
⚙️ CPU: {get_cpu()}%
🧠 RAM: {get_ram()}%
💾 DISK: {get_disk()}%
"""

    await update.message.reply_text(text)


# =====================
# BUTTONS
# =====================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "status":
        await q.edit_message_text(
            f"""🖥 STATUS

IP: {get_ip()}
CPU: {get_cpu()}%
RAM: {get_ram()}%
DISK: {get_disk()}%"""
        )

    if q.data == "users":
        rows = db.get_users()
        msg = "👤 USERS:\n\n"
        for u in rows:
            msg += f"{u[0]} | {u[1]} | {u[2]}\n"

        await q.edit_message_text(msg)

    if q.data == "cmds":
        await q.edit_message_text(
            "/start\n/create\n/users\n/status"
        )


# =====================
# BUILD BOT (FIX PRINCIPAL)
# =====================
def build_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(buttons))

    return app