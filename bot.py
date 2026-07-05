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
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "127.0.0.1"


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
        [InlineKeyboardButton("📋 CMDS", callback_data="cmds")],
    ]

    await update.message.reply_text(
        "🚀 CHOMELO SaaS ONLINE\n\nSistema activo correctamente",
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
        days = int(context.args[2])

        expire = (datetime.now() + timedelta(days=days)).isoformat()

        db.create_user(user, password, expire)

        await update.message.reply_text(
            f"✅ USER CREADO\n\n"
            f"👤 Usuario: {user}\n"
            f"🔑 Password: {password}\n"
            f"📅 Expira en: {days} días"
        )

    except Exception as e:
        await update.message.reply_text(
            "❌ Uso incorrecto\n\n/create user pass dias"
        )


# =====================
# LIST USERS
# =====================
async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ No autorizado")

    rows = db.get_users()

    if not rows:
        return await update.message.reply_text("📭 No hay usuarios")

    msg = "👤 USERS:\n\n"

    for u in rows:
        msg += f"👤 {u[0]} | 🔑 {u[1]} | 📅 {u[2]}\n"

    await update.message.reply_text(msg)


# =====================
# STATUS VPS
# =====================
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = (
        "🖥 CHOMELO VPS STATUS\n\n"
        f"🌐 IP: {get_ip()}\n"
        f"⚙️ CPU: {get_cpu()}%\n"
        f"🧠 RAM: {get_ram()}%\n"
        f"💾 DISK: {get_disk()}%\n\n"
        "✔ Sistema estable"
    )

    await update.message.reply_text(msg)


# =====================
# BUTTONS
# =====================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "status":
        await query.edit_message_text(
            f"""🖥 STATUS

🌐 IP: {get_ip()}
⚙️ CPU: {get_cpu()}%
🧠 RAM: {get_ram()}%
💾 DISK: {get_disk()}%"""
        )

    elif query.data == "users":

        rows = db.get_users()

        if not rows:
            await query.edit_message_text("📭 No hay usuarios")
            return

        msg = "👤 USERS:\n\n"

        for u in rows:
            msg += f"👤 {u[0]} | 🔑 {u[1]} | 📅 {u[2]}\n"

        await query.edit_message_text(msg)

    elif query.data == "cmds":

        await query.edit_message_text(
            "/start - iniciar\n"
            "/create user pass days\n"
            "/users - listar usuarios\n"
            "/status - estado VPS"
        )


# =====================
# BUILD BOT (PRO STABLE)
# =====================
def build_bot():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(buttons))

    return app