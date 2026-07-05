from bot import build_bot

if __name__ == "__main__":
    app = build_bot()
    app.run_polling()