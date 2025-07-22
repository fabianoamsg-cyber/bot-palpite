import os
import logging
import asyncio
from telegram import Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CallbackContext
import aiohttp
from datetime import datetime

# Configurações
BOT_TOKEN = os.getenv("BOT_TOKEN")
GRUPO_ID = os.getenv("GRUPO_ID")  # Ex: '-1002814723832'
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

# Log
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def obter_palpite():
    url = "https://v3.football.api-sports.io/fixtures?next=10"
    headers = {
        "x-apisports-key": API_FOOTBALL_KEY
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            dados = await response.json()

    palpites = []
    for jogo in dados["response"]:
        teams = jogo["teams"]
        fixture = jogo["fixture"]
        date = datetime.fromisoformat(fixture["date"].replace("Z", "+00:00")).strftime("%d/%m %H:%M")
        palpites.append(
            f"📅 *{date}*\n⚽ *{teams['home']['name']}* vs *{teams['away']['name']}*\nAposta: *Over 1.5 Gols* ✅"
        )

    return "\n\n".join(palpites[:5]) if palpites else "Sem jogos disponíveis."

async def enviar_mensagem(context: CallbackContext):
    texto = await obter_palpite()
    await context.bot.send_message(chat_id=GRUPO_ID, text=texto, parse_mode="Markdown")

async def start_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Envia a cada 30 minutos
    application.job_queue.run_repeating(enviar_mensagem, interval=1800, first=5)

    print("Bot iniciado...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()

if __name__ == '__main__':
    asyncio.run(start_bot())
