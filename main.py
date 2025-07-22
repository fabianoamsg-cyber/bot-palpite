import os
import time
import requests
import telebot
from flask import Flask, request
from threading import Thread

# Variáveis de ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
GRUPO_ID = os.getenv("GRUPO_ID")
API_KEY = os.getenv("API_FOOTBALL_KEY")

# Inicialização do bot e Flask
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Tipos de apostas
TIPOS_APOSTA = {
    "Over 1.5": "over_15",
    "Over 2.5": "over_25",
    "Over 3.5": "over_35",
    "Ambas Marcam": "btts",
    "Vitória": "1x2",
    "Empate": "draw",
    "Placar Exato": "exact_score"
}

# Buscar próximos jogos da API-Football
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
        print("❌ Erro ao buscar jogos:", e)
        return []

# Gera bilhetes com até 5 jogos por tipo
def gerar_bilhetes(jogos):
    bilhetes = {tipo: [] for tipo in TIPOS_APOSTA}
    for jogo in jogos:
        nome = f"{jogo['teams']['home']['name']} x {jogo['teams']['away']['name']}"
        for tipo in TIPOS_APOSTA:
            if len(bilhetes[tipo]) < 5:
                bilhetes[tipo].append(f"🔹 {nome}")
    return bilhetes

# Envia os bilhetes para o canal
def enviar_bilhetes():
    jogos = buscar_jogos()
    if not jogos:
        print("⚠️ Nenhum jogo encontrado.")
        return

    bilhetes = gerar_bilhetes(jogos)

    for tipo, lista in bilhetes.items():
        if lista:
            texto = f"🏆 *Bilhete - {tipo}*\n\n"
            texto += "\n".join(lista)
            texto += "\n\n🎯 *Confiança:* Alta\n#Palpites #Futebol"
            try:
                bot.send_message(chat_id=GRUPO_ID, text=texto, parse_mode="Markdown")
                print(f"✅ Bilhete enviado - {tipo}")
                time.sleep(3)
            except Exception as e:
                print(f"❌ Erro ao enviar bilhete {tipo}:", e)

# Loop contínuo a cada 30 minutos
def iniciar_envio_continuo():
    while True:
        enviar_bilhetes()
        time.sleep(1800)  # 30 minutos

# Rota padrão do Flask (Render)
@app.route("/")
def home():
    return "✅ Bot de Palpites está rodando!"

# Webhook do Telegram
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
  enviar_bilhetes()  # <- ENVIO DE TESTE IMEDIATO


# Inicia tudo
if __name__ == "__main__":
    webhook_url = os.getenv("RENDER_EXTERNAL_URL", "") + "/" + BOT_TOKEN

    try:
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        print(f"✅ Webhook definido: {webhook_url}")
    except Exception as e:
        print(f"❌ Erro ao definir webhook: {e}")

    try:
        enviar_bilhetes()  # Envio de teste imediato
    except Exception as e:
        print(f"❌ Erro no envio de teste imediato: {e}")

    try:
        Thread(target=iniciar_envio_continuo).start()
        print("📡 Envio contínuo iniciado")
    except Exception as e:
        print(f"❌ Erro ao iniciar loop contínuo: {e}")

    try:
        app.run(host="0.0.0.0", port=10000)
    except Exception as e:
        print(f"❌ Erro ao iniciar Flask: {e}")
