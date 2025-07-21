import os
import time
import requests
import telebot
from flask import Flask
from threading import Thread

# Variáveis de ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
GRUPO_ID = os.getenv("GRUPO_ID")
API_KEY = os.getenv("API_FOOTBALL_KEY")

# Inicialização
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

TIPOS_APOSTA = {
    "Over 1.5": "over_15",
    "Over 2.5": "over_25",
    "Over 3.5": "over_35",
    "Ambas Marcam": "btts",
    "Vitória": "1x2",
    "Empate": "draw",
    "Placar Exato": "exact_score"
}

def buscar_jogos():
    url = "https://v3.football.api-sports.io/fixtures?next=50"
    headers = {
        "x-apisports-key": API_KEY
    }
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data['response']
    except Exception as e:
        print("Erro ao buscar jogos:", e)
        return []

def gerar_bilhetes(jogos):
    bilhetes = {tipo: [] for tipo in TIPOS_APOSTA}
    for jogo in jogos:
        for tipo in TIPOS_APOSTA:
            if len(bilhetes[tipo]) < 5:
                nome = f"{jogo['teams']['home']['name']} x {jogo['teams']['away']['name']}"
                bilhetes[tipo].append(f"🔹 {nome}")
    return bilhetes

def enviar_bilhetes():
    jogos = buscar_jogos()
    if not jogos:
        print("Nenhum jogo encontrado.")
        return

    bilhetes = gerar_bilhetes(jogos)

    for tipo, jogos in bilhetes.items():
        if jogos:
            texto = f"🏆 *Bilhete - {tipo}*\n\n"
            texto += "\n".join(jogos)
            texto += "\n\n🎯 *Confiança:* Alta\n#Palpites #Futebol"
            try:
                bot.send_message(chat_id=GRUPO_ID, text=texto, parse_mode="Markdown")
                time.sleep(3)
            except Exception as e:
                print(f"Erro ao enviar {tipo}: {e}")

def iniciar_envio_continuo():
    while True:
        enviar_bilhetes()
        time.sleep(1800)  # Aguarda 30 minutos para próximo envio

# Flask apenas para manter online no Render
@app.route('/')
def home():
    return 'Bot de Palpites está rodando!'

def iniciar_flask():
    app.run(host='0.0.0.0', port=10000)

if __name__ == '__main__':
    Thread(target=iniciar_envio_continuo).start()
    iniciar_flask()
