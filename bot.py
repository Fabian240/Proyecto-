import psutil
import socket
from datetime import datetime, timedelta

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


# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 STATUS", callback_data="status")],
        [InlineKeyboardButton("📋 CMD", callback_data="cmds")]
    ]

    await update.message.reply_text(
        "🚀 CHOMELO v1 ONLINE",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# CREATE USER
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ No autorizado")

    try:
        user = context.args[0]
        password = context.args[1]
        minutes = int(context.args[2])

        expire = (datetime.now() + timedelta(minutes=minutes)).isoformat()

        db.create_user(user, password, expire)

        await update.message.reply_text(
            f"✅ USER CREADO\n{user}\nExpira: {minutes} min"
        )

    except:
        await update.message.reply_text("❌ Uso: /create user pass minutos")


# USERS
async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = db.get_users()

    msg = "👤 USERS:\n\n"
    for u in data:
        msg += f"{u['user']} | {u['password']} | {u['expire']}\n"

    await update.message.reply_text(msg)


# STATUS
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"IP: {get_ip()}\nCPU: {get_cpu()}%\nRAM: {get_ram()}%"
    )


# CALLBACK BUTTONS
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "status":
        await q.edit_message_text(
            f"IP: {get_ip()}\nCPU: {get_cpu()}%\nRAM: {get_ram()}%"
        )

    if q.data == "cmds":
        await q.edit_message_text("/start /create /users /status")


def build_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(buttons))

    return app