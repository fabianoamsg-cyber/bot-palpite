import os
import telebot
import requests
import random
import time
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_FOOTBALL_KEY")
GRUPO_ID = os.getenv("GRUPO_ID")

bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

URL_API = "https://v3.football.api-sports.io/fixtures"

TIPOS = {
    "Over 1.5": lambda: "Mais de 1.5 gols",
    "Over 2.5": lambda: "Mais de 2.5 gols",
    "Over 3.5": lambda: "Mais de 3.5 gols",
    "Ambas Marcam": lambda: "Ambas as equipes marcam",
    "Vitória": lambda: "Vitória do time favorito",
    "Empate": lambda: "Empate no tempo normal",
    "Placar Exato": lambda: f"{random.randint(1, 3)}x{random.randint(0, 2)}"
}

def buscar_jogos():
    headers = {"x-apisports-key": API_KEY}
    params = {"date": time.strftime("%Y-%m-%d"), "timezone": "America/Sao_Paulo"}
    r = requests.get(URL_API, headers=headers, params=params)
    if r.status_code == 200:
        data = r.json()
        return data.get("response", [])
    else:
        print("Erro na API:", r.text)
        return []

def montar_bilhete(jogos, tipo_aposta, max_jogos=5):
    random.shuffle(jogos)
    bilhete = [f"📊 *Bilhete {tipo_aposta}*\n"]
    count = 0
    for j in jogos:
        try:
            home = j['teams']['home']['name']
            away = j['teams']['away']['name']
            hora = j['fixture']['date'][11:16]
            aposta = TIPOS[tipo_aposta]()
            bilhete.append(f"🕒 {hora} — {home} vs {away}\n🔹 Aposta: *{aposta}*\n")
            count += 1
            if count == max_jogos:
                break
        except:
            continue
    return "\n".join(bilhete) if count else None

def enviar_bilhetes():
    jogos = buscar_jogos()
    if not jogos:
        bot.send_message(GRUPO_ID, "⚠️ Nenhum jogo disponível no momento.")
        return
    for tipo in TIPOS:
        bilhete = montar_bilhete(jogos, tipo)
        if bilhete:
            bot.send_message(GRUPO_ID, bilhete, parse_mode="Markdown")
        time.sleep(1)

@app.route("/")
def home():
    return "Bot de Palpites ON"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

def iniciar_webhook():
    url = os.getenv("RENDER_EXTERNAL_URL") or "https://bot-palpite-2.onrender.com"
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"{url}/{BOT_TOKEN}")

def loop_continuo():
    while True:
        try:
            enviar_bilhetes()
            time.sleep(1800)  # 30 minutos
        except Exception as e:
            print("Erro no loop:", e)
            time.sleep(60)

if __name__ == "__main__":
    from threading import Thread
    Thread(target=loop_continuo).start()
    iniciar_webhook()
    app.run(host="0.0.0.0", port=10000)
