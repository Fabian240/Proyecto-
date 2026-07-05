import psutil
import socket
import logging
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
# LOGGING (IMPORTANTE)
# =====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =====================
# SYSTEM INFO
# =====================
def get_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "127.0.0.1"

def get_cpu():
    return psutil.cpu_percent(interval=0.5)

def get_ram():
    return psutil.virtual_memory().percent

def get_disk():
    return psutil.disk_usage('/').percent


# =====================
# SAFE WRAPPER (CLAVE)
# =====================
async def safe_send(update, text):
    try:
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"⚠️ ERROR: {e}")


# =====================
# START
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        keyboard = [
            [InlineKeyboardButton("📊 STATUS", callback_data="status")],
            [InlineKeyboardButton("👤 USERS", callback_data="users")],
            [InlineKeyboardButton("🧪 DEBUG", callback_data="debug")],
        ]

        await update.message.reply_text(
            "🚀 CHOMELO SaaS PRO ONLINE",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    except Exception as e:
        await safe_send(update, f"start error: {e}")


# =====================
# CREATE USER
# =====================
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != ADMIN_ID:
            return await update.message.reply_text("⛔ No autorizado")

        user = context.args[0]
        password = context.args[1]
        days = int(context.args[2])

        expire = (datetime.now() + timedelta(days=days)).isoformat()

        db.create_user(user, password, expire)

        await update.message.reply_text(
            f"✅ USER CREADO\n\n👤 {user}\n📅 {days} días"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ create error: {e}")


# =====================
# USERS
# =====================
async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != ADMIN_ID:
            return await update.message.reply_text("⛔ No autorizado")

        rows = db.get_users()

        if not rows:
            return await update.message.reply_text("📭 No users")

        msg = "👤 USERS:\n\n"

        for u in rows:
            msg += f"{u[0]} | {u[1]} | {u[2]}\n"

        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"users error: {e}")


# =====================
# STATUS VPS
# =====================
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = f"""
🖥 CHOMELO STATUS

🌐 IP: {get_ip()}
⚙️ CPU: {get_cpu()}%
🧠 RAM: {get_ram()}%
💾 DISK: {get_disk()}%

✔ ONLINE
"""
        await update.message.reply_text(msg)

    except Exception as e:
        await safe_send(update, f"status error: {e}")


# =====================
# DEBUG COMMAND (NUEVO)
# =====================
async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        import os

        info = f"""
🧪 DEBUG SYSTEM

Python OK
PID: {os.getpid()}
CPU: {get_cpu()}%
RAM: {get_ram()}%
Disk: {get_disk()}%
"""
        await update.message.reply_text(info)

    except Exception as e:
        await safe_send(update, f"debug error: {e}")


# =====================
# BUTTONS
# =====================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
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

        elif q.data == "users":
            rows = db.get_users()
            msg = "👤 USERS:\n\n"
            for u in rows:
                msg += f"{u[0]} | {u[1]} | {u[2]}\n"
            await q.edit_message_text(msg)

        elif q.data == "debug":
            await q.edit_message_text("🧪 DEBUG OK")

    except Exception as e:
        await q.edit_message_text(f"callback error: {e}")


# =====================
# BUILD BOT
# =====================
def build_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("debug", debug))
    app.add_handler(CallbackQueryHandler(buttons))

    return app