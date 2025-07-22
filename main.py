import os
from flask import Flask
from threading import Thread
import telebot
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
GRUPO_ID = os.getenv("GRUPO_ID")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def enviar_teste():
    try:
        mensagem = "🟢 Teste de funcionamento do bot.\n\n✅ Se você recebeu isso, o bot está funcionando perfeitamente!"
        bot.send_message(GRUPO_ID, mensagem)
        print("✅ Mensagem de teste enviada com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem de teste: {e}")

@app.route('/')
def index():
    return 'Bot de Teste Ativo!'

def iniciar_flask():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    Thread(target=enviar_teste).start()
    iniciar_flask()
