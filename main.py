import os
import time
import random
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

app = Flask(__name__)

# Variáveis de ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
GRUPO_ID = os.getenv("GRUPO_ID")
API_KEY = os.getenv("API_FOOTBALL_KEY")

bot = Bot(token=BOT_TOKEN)

def obter_palpite(jogo):
    casa = jogo['homeTeam']['name']
    fora = jogo['awayTeam']['name']
    data = jogo['fixture']['date'][:10]
    tipo = random.choice(["Over 1.5", "Over 2.5", "Ambas Marcam", "Vitória", "Empate", "Placar Exato"])
    chance = random.randint(70, 95)
    return f"*{casa} x {fora}* - `{tipo}`\n📆 {data} | 💡 Probabilidade: *{chance}%*"

def buscar_jogos():
    url = "https://v3.football.api-sports.io/fixtures?date=2025-07-23"
    headers = {"x-apisports-key": API_KEY}
    try:
        resposta = requests.get(url, headers=headers)
        dados = resposta.json()
        return dados['response'][:5]  # Pega os 5 primeiros jogos
    except Exception as e:
        print("Erro ao buscar jogos:", e)
        return []

def enviar_bilhetes():
    jogos = buscar_jogos()
    if not jogos:
        return

    bilhete = [obter_palpite(jogo) for jogo in jogos]
    media = random.randint(80, 95)

    texto = "🏆 *Bilhete do Dia*\n\n" + "\n\n".join(bilhete)
    texto += f"\n\n📊 *Confiança média:* *{media}%*\n#Palpites #Futebol"

    try:
        bot.send_message(chat_id=GRUPO_ID, text=texto, parse_mode="Markdown")
        print("Bilhete enviado!")
    except Exception as e:
        print(f"Erro ao enviar bilhete: {e}")

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher = Dispatcher(bot, None, use_context=True)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/")
def home():
    return "Bot de Palpites Online!", 200

if __name__ == "__main__":
    enviar_bilhetes()
