import threading
import uvicorn

from bot import build_bot
from api import app

def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":

    # API en background
    threading.Thread(target=start_api, daemon=True).start()

    # BOT (IMPORTANTE: esto bloquea y mantiene vivo el bot)
    bot = build_bot()
    bot.run_polling()