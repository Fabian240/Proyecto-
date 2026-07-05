import threading
import uvicorn

from bot.bot import build_bot
from api.app import app
from tasks.scheduler import start_tasks


def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    start_tasks()

    threading.Thread(target=start_api, daemon=True).start()

    bot = build_bot()
    bot.run_polling()