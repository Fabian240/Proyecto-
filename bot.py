import psutil
import socket
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

from config import BOT_TOKEN, ADMIN_ID
import db


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
# PANEL
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📊 STATUS", callback_data="status")],
        [InlineKeyboardButton("👤 USERS", callback_data="users")],
        [InlineKeyboardButton("➕ CREATE", callback_data="create")],
        [InlineKeyboardButton("🟢 ACTIVE", callback_data="active")],
        [InlineKeyboardButton("⛔ SUSPEND", callback_data="suspend")],
        [InlineKeyboardButton("🗑 DELETE", callback_data="delete")],
        [InlineKeyboardButton("🔄 REFRESH", callback_data="refresh")],
    ]

    await update.message.reply_text(
        "🚀 SAAS HOSTING PANEL PRO",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


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

        await update.message.reply_text(f"✅ USER CREADO: {user}")

    except:
        await update.message.reply_text("Uso: /create user pass days")


# =====================
# USERS
# =====================
async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):

    rows = db.get_users()

    if not rows:
        return await update.message.reply_text("📭 No users")

    msg = "👤 USERS:\n\n"

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
# BUTTONS (SAAS CORE)
# =====================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    data = q.data


    # ---------------- STATUS
    if data == "status":
        await q.edit_message_text(
            f"""🖥 STATUS

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


    # ---------------- ACTIVE
    elif data == "active":
        rows = db.get_users()

        msg = "🟢 ACTIVE USERS:\n\n"
        for u in rows:
            if u[3] == "ACTIVE":
                msg += f"{u[0]} | {u[2]}\n"

        await q.edit_message_text(msg)


    # ---------------- SUSPEND (SIMULADO PANEL)
    elif data == "suspend":
        await q.edit_message_text(
            "⛔ Usa: /suspend user\n(Siguiente upgrade lo automatizo)"
        )


    # ---------------- DELETE (SIMULADO PANEL)
    elif data == "delete":
        await q.edit_message_text(
            "🗑 Usa: /delete user\n(Siguiente upgrade lo automatizo)"
        )


    # ---------------- CREATE MENU
    elif data == "create":
        await q.edit_message_text("➕ Usa:\n/create user pass days")


    # ---------------- REFRESH
    elif data == "refresh":
        await q.edit_message_text("🔄 Panel actualizado")


# =====================
# BUILD BOT
# =====================
def build_bot():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("status", status))

    app.add_handler(CallbackQueryHandler(buttons))

    return app