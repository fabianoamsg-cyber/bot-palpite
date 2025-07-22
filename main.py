import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
GRUPO_ID = os.getenv("GRUPO_ID")
bot = Bot(token=TOKEN)

app = Flask(__name__)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bot de palpites iniciado!")

def webhook_handler(request_data):
    update = Update.de_json(request_data, bot)
    dispatcher.process_update(update)
    return "ok"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    return webhook_handler(request.get_json(force=True))

@app.route("/")
def home():
    return "Bot de Palpites está online!"

dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", start))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
