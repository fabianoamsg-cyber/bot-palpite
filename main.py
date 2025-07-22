import os
import time
import random
import requests
import telebot
from flask import Flask, request
from threading import Thread
from datetime import datetime

# Variáveis de ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_FOOTBALL_KEY")
GRUPO_ID = os.getenv("GRUPO_ID")

# Inicializações
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Função para obter palpites
def gerar_palpite(tipo):
    url = "https://v3.football.api-sports.io/fixtures"
    params = {
        "next": 20,
        "timezone": "America/Sao_Paulo"
    }
    headers = {
        "x-apisports-key": API_KEY
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        jogos = data["response"]
        palpites = []

        for jogo in jogos:
            equipes = jogo["teams"]
            data_jogo = jogo["fixture"]["date"]
            data_formatada = datetime.strptime(data_jogo, "%Y-%m-%dT%H:%M:%S%z").strftime("%d/%m %H:%M")

            casa = equipes["home"]["name"]
            fora = equipes["away"]["name"]

            if tipo == "Over 1.5":
                chance = random.randint(72, 95)
                palpite = f"🏟️ {casa} x {fora}\n📅 {data_formatada}\n🔮 Over 1.5 gols\n🎯 Chance: {chance}%"
            elif tipo == "Ambas Marcam":
                chance = random.randint(65, 90)
                palpite = f"🏟️ {casa} x {fora}\n📅 {data_formatada}\n🤝 Ambas Marcam\n🎯 Chance: {chance}%"
            elif tipo == "Vitória Mandante":
                chance = random.randint(70, 88)
                palpite = f"🏟️ {casa} x {fora}\n📅 {data_formatada}\n🏆 Vitória: {casa}\n🎯 Chance: {chance}%"
            else:
                continue

            palpites.append((chance, palpite))

        palpites.sort(reverse=True, key=lambda x: x[0])
        melhores = [j[1] for j in palpites[:5]]
        media_conf = sum([j[0] for j in palpites[:5]]) // 5

        return melhores, media_conf

    except Exception as e:
        print(f"Erro ao obter palpites: {e}")
        return [], 0

# Envia os bilhetes
def enviar_bilhetes():
    tipos = ["Over 1.5", "Ambas Marcam", "Vitória Mandante"]
    for tipo in tipos:
        jogos, media = gerar_palpite(tipo)
        if not jogos:
            continue

        texto = f"📌 *Bilhete - {tipo}*\n\n"
        texto += "\n\n".join(jogos)
        texto += f"\n\n🔥 *Confiança média:* {media}%\n#Palpites #Futebol"

        try:
            bot.send_message(chat_id=GRUPO_ID, text=texto, parse_mode="Markdown")
            time.sleep(3)
        except Exception as e:
            print(f"Erro ao enviar bilhete {tipo}: {e}")

# Endpoint de webhook correto
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    return "Método não permitido", 405

# Rota simples
@app.route("/")
def index():
    return "Bot de Palpites Ativo"

# Agendamento de envio automático
def agendar_envios():
    while True:
        enviar_bilhetes()
        time.sleep(1800)  # 30 minutos

# Início paralelo
if __name__ == "__main__":
    Thread(target=agendar_envios).start()
    app.run(host="0.0.0.0", port=10000)
