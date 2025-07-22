import os
import time
import requests
import telebot
from flask import Flask, request
from threading import Thread

# Variáveis de ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_FOOTBALL_KEY")
GRUPO_ID = os.getenv("GRUPO_ID")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Tipos de aposta suportados
TIPOS_APOSTA = [
    "Over 1.5",
    "Over 2.5",
    "Over 3.5",
    "Ambas Marcam",
    "Vitória (1x2)",
    "Empate",
    "Placar Exato"
]

# Gera bilhete com 5 jogos do tipo especificado
def gerar_bilhete(tipo):
    url = f"https://v3.football.api-sports.io/odds?bet={tipo}&timezone=America/Sao_Paulo"
    headers = {
        "x-apisports-key": API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        bilhete = []
        jogos_usados = set()

        for resultado in data.get("response", []):
            if len(bilhete) >= 5:
                break
            jogo = resultado.get("league", {}).get("name", "") + " - "
            jogo += resultado.get("teams", {}).get("home", {}).get("name", "") + " x "
            jogo += resultado.get("teams", {}).get("away", {}).get("name", "")

            if jogo not in jogos_usados:
                jogos_usados.add(jogo)
                bilhete.append(f"• {jogo}")

        return bilhete
    except Exception as e:
        print(f"Erro ao gerar bilhete: {e}")
        return []

# Envia um bilhete de um tipo (ex: Over 2.5)
def enviar_bilhetes():
    try:
        tipo = "Over 2.5"  # Pode variar se quiser testar outro
        bilhete = gerar_bilhete(tipo)
        if bilhete:
            mensagem = f"🔥 Bilhete - {tipo}\n\n" + "\n".join(bilhete)
            bot.send_message(GRUPO_ID, mensagem)
            print("✅ Bilhete enviado")
        else:
            print("⚠️ Nenhum bilhete gerado")
    except Exception as e:
        print(f"❌ Erro ao enviar bilhete: {e}")

# Loop de envio automático a cada 30 minutos
def iniciar_envio_continuo():
    print("🚀 Envio contínuo iniciado")
    while True:
        enviar_bilhetes()
        time.sleep(1800)

# Webhook do Telegram
@app.route(f'/{BOT_TOKEN}', methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return '', 200

@app.route('/')
def index():
    return 'Bot de Palpites funcionando!'

# Iniciar Flask
def iniciar_flask():
    app.run(host="0.0.0.0", port=10000)

# Início da aplicação
if __name__ == "__main__":
    webhook_url = f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)

    def iniciar_tudo():
        enviar_bilhetes()  # ENVIO IMEDIATO
        iniciar_envio_continuo()

    Thread(target=iniciar_tudo).start()
    iniciar_flask()
