import psutil
import socket
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

from config import BOT_TOKEN, ADMIN_ID
import db

def get_ip():
    return socket.gethostbyname(socket.gethostname())

def get_cpu():
    return psutil.cpu_percent()

def get_ram():
    return psutil.virtual_memory().percent

def get_disk():
    return psutil.disk_usage('/').percent

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 STATUS", callback_data="status")],
        [InlineKeyboardButton("👤 USERS", callback_data="users")]
    ]

    await update.message.reply_text(
        "🚀 CHOMELO v1 PRO ONLINE",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# CREATE USER
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ No autorizado")

    try:
        user = context.args[0]
        password = context.args[1]
        expire = context.args[2]  # formato: 26/05/2026

        db.create_user(user, password, expire)

        await update.message.reply_text(
            f"✅ Usuario creado\n👤 {user}\n📅 Expira: {expire}"
        )
    except:
        await update.message.reply_text("❌ Uso: /create user pass dd/mm/yyyy")

# LIST USERS
async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = db.get_users()

    msg = "👤 USERS:\n\n"
    for u in data:
        msg += f"User: {u[0]} | Pass: {u[1]} | Exp: {u[2]}\n"

    await update.message.reply_text(msg)

# STATUS VPS
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = f"""
🖥 VPS STATUS

IP: {get_ip()}
CPU: {get_cpu()}%
RAM: {get_ram()}%
DISK: {get_disk()}%
"""
    await update.message.reply_text(msg)

# BUTTONS
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "status":
        await q.edit_message_text(
            f"IP: {get_ip()}\nCPU: {get_cpu()}%\nRAM: {get_ram()}%\nDISK: {get_disk()}%"
        )

    if q.data == "users":
        data = db.get_users()
        text = "\n".join([f"{u[0]} | {u[2]}" for u in data])
        await q.edit_message_text(text)

def build_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CallbackQueryHandler(buttons))

    return app