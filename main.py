import threading
import uvicorn

from bot import build_bot
from api import app

# --- API THREAD ---
def start_api():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":

    # 1. Iniciar API en segundo plano
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    print("API iniciada en puerto 8000")

    # 2. Iniciar BOT Telegram (bloqueante)
    bot = build_bot()

    print("Bot iniciado correctamente")

    bot.run_polling(
        drop_pending_updates=True  # 🔥 limpia /start atascados
    )