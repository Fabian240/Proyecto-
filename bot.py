import psutil
import socket
import logging
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

from config import BOT_TOKEN, ADMIN_ID
import db


# =====================
# LOGGING PRO
# =====================
logging.basicConfig(level=logging.INFO)


# =====================
# SYSTEM INFO VPS
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
# PANEL PRINCIPAL
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📊 STATUS VPS", callback_data="status")],
        [InlineKeyboardButton("👤 USERS", callback_data="users")],
        [InlineKeyboardButton("➕ CREATE", callback_data="create")],
        [InlineKeyboardButton("🟢 ACTIVE USERS", callback_data="active")],
        [InlineKeyboardButton("⛔ SUSPEND USER", callback_data="suspend")],
        [InlineKeyboardButton("🗑 DELETE USER", callback_data="delete")],
        [InlineKeyboardButton("🔄 REFRESH", callback_data="refresh")],
        [InlineKeyboardButton("🧪 DEBUG", callback_data="debug")],
    ]

    await update.message.reply_text(
        "🚀 CHOMELO SAAS ULTRA PANEL",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =====================
# CREATE USER (CMD)
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

        await update.message.reply_text(f"✅ USER CREATED: {user}")

    except Exception as e:
        await update.message.reply_text(f"CREATE ERROR: {e}")


# =====================
# USERS LIST
# =====================
async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):

    rows = db.get_users()

    if not rows:
        return await update.message.reply_text("📭 NO USERS")

    msg = "👤 USERS LIST:\n\n"

    for u in rows:
        msg += f"{u[0]} | {u[1]} | {u[2]} | {u[3]}\n"

    await update.message.reply_text(msg)


# =====================
# STATUS VPS
# =====================
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = f"""
🖥 VPS STATUS

IP: {get_ip()}
CPU: {get_cpu()}%
RAM: {get_ram()}%
DISK: {get_disk()}%
"""

    await update.message.reply_text(msg)


# =====================
# DEBUG PANEL (NUEVO)
# =====================
async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):

    import os

    msg = f"""
🧪 DEBUG SYSTEM

PID: {os.getpid()}
CPU: {get_cpu()}%
RAM: {get_ram()}%
DISK: {get_disk()}%
TIME: {datetime.now()}
"""

    await update.message.reply_text(msg)


# =====================
# CALLBACK BUTTONS (ULTRA PANEL)
# =====================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    data = q.data

    print("BUTTON CLICKED:", data)


    # ---------------- STATUS
    if data == "status":
        await q.edit_message_text(
            f"""🖥 STATUS VPS

IP: {get_ip()}
CPU: {get_cpu()}%
RAM: {get_ram()}%
DISK: {get_disk()}%"""
        )


    # ---------------- USERS
    elif data == "users":

        rows = db.get_users()

        msg = "👤 USERS:\n\n"

        for u in rows:
            msg += f"{u[0]} | {u[1]} | {u[2]} | {u[3]}\n"

        await q.edit_message_text(msg)


    # ---------------- ACTIVE USERS
    elif data == "active":

        rows = db.get_users()

        msg = "🟢 ACTIVE USERS:\n\n"

        for u in rows:
            if u[3] == "ACTIVE":
                msg += f"{u[0]} | {u[2]}\n"

        await q.edit_message_text(msg)


    # ---------------- SUSPEND (SIMULADO PRO)
    elif data == "suspend":
        await q.edit_message_text(
            "⛔ USE:\n/suspend username\n\n(Upgrade DB para acción real)"
        )


    # ---------------- DELETE (SIMULADO PRO)
    elif data == "delete":
        await q.edit_message_text(
            "🗑 USE:\n/delete username\n\n(Upgrade DB para acción real)"
        )


    # ---------------- CREATE INFO
    elif data == "create":
        await q.edit_message_text("➕ USE:\n/create user pass days")


    # ---------------- REFRESH
    elif data == "refresh":
        await q.edit_message_text("🔄 PANEL REFRESHED ✔")


    # ---------------- DEBUG
    elif data == "debug":
        await q.edit_message_text("🧪 DEBUG ACTIVE ✔")


# =====================
# BUILD BOT (FINAL FIXED)
# =====================
def build_bot():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("debug", debug))

    # 🔥 IMPORTANT FIX PARA BOTONES
    app.add_handler(CallbackQueryHandler(buttons, pattern=".*"))

    return app