from flask import Flask
from threading import Thread
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ENV variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

# -------- Flask server (Railway ko zinda rakhne ke liye) --------
app_web = Flask(__name__)

@app_web.route("/")
def home():
    return "Bot is alive"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host="0.0.0.0", port=port)

# -------- Telegram Bot --------
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text

        headers = {
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are ReplyShastra AI. Generate ONLY the final reply message. No explanations."},
                {"role": "user", "content": user_message}
            ]
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )

        reply_text = response.json()["choices"][0]["message"]["content"]

        await update.message.reply_text(reply_text)

    except Exception as e:
        await update.message.reply_text("Thoda error aa gaya 😅 fir se bhej na.")

# -------- Run both together --------
Thread(target=run_web).start()

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

print("Bot started...")
app.run_polling()
