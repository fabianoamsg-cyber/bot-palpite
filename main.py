import os
import time
import requests
import telebot
from flask import Flask, request

# Variáveis de ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
GRUPO_ID = os.getenv("GRUPO_ID")  # Ex: -1002814723832
API_KEY = os.getenv("API_FOOTBALL_KEY")

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
    headers = {"x-apisports-key": API_KEY}
    try:
        response = requests.get(url, headers=headers)
        return response.json().get('response', [])
    except Exception as e:
        print(f"Erro ao buscar jogos: {e}")
        return []

def gerar_bilhetes(jogos):
    bilhetes = {tipo: [] for tipo in TIPOS_APOSTA}
    for jogo in jogos:
        data_jogo = jogo['fixture']['date'].split("T")[0]
        home = jogo['teams']['home']['name']
        away = jogo['teams']['away']['name']
        nome = f"{home} x {away}"
        probabilidade_jogo = f"{round(60 + 40 * (hash(nome) % 100) / 100)}%"  # Simulação

        for tipo in TIPOS_APOSTA:
            if len(bilhetes[tipo]) < 5:
                bilhetes[tipo].append(f"📅 {data_jogo} - {nome} | 🔮 Chance: {probabilidade_jogo}")
    return bilhetes

def enviar_bilhetes():
    jogos = buscar_jogos()
    if not jogos:
        print("Nenhum jogo encontrado.")
        return

    bilhetes = gerar_bilhetes(jogos)

    for tipo, jogos_bilhete in bilhetes.items():
        if jogos_bilhete:
            texto = f"🏆 *Bilhete - {tipo}*\n\n"
            texto += "\n".join(jogos_bilhete)
            texto += "\n\n🎯 *Confiança média:* 82%\n#Palpites #Futebol"
            try:
                bot.send_message(chat_id=GRUPO_ID, text=texto, parse_mode="Markdown")
                time.sleep(3)
            except Exception as e:
                print(f"Erro ao enviar {tipo}: {e}")

# Endpoint para Webhook
@app.route('/', methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'OK', 405

# Rota simples
@app.route("/")
def index():
    return "Bot de Palpites no Ar!"

# Loop de envio automático
def agendar_envios():
    while True:
        enviar_bilhetes()
        time.sleep(1800)  # 30 minutos

if __name__ == "__main__":
    import threading
    threading.Thread(target=agendar_envios).start()
    app.run(host="0.0.0.0", port=10000)
