import telebot
import requests
import os
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")
GRUPO_ID = os.getenv("GRUPO_ID")  # ex: -1002814723832
API_KEY = os.getenv("API_FOOTBALL_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot de Palpites está online!", 200

def get_palpite():
    url = "https://v3.football.api-sports.io/fixtures?next=5"
    headers = {
        "x-apisports-key": API_KEY
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    palpites = []
    for jogo in data.get("response", []):
        times = jogo["teams"]
        home = times["home"]["name"]
        away = times["away"]["name"]
        palpites.append(f"🔮 *Palpite:* {home} x {away}\n➡️ *Over 1.5 Gols*\n")

    return "\n".join(palpites) if palpites else "Nenhum palpite no momento."

@app.route("/send", methods=["GET"])
def send():
    texto = get_palpite()
    bot.send_message(GRUPO_ID, texto, parse_mode="Markdown")
    return "Enviado", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://bot-palpite.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=10000)
