import os
import logging
import aiohttp
from telegram import Bot
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import pytz

TOKEN = os.getenv("BOT_TOKEN")
CANAL_ID = os.getenv("GRUPO_ID")
API_KEY = os.getenv("API_FOOTBALL_KEY")

# Configure o fuso horário do Brasil
fuso_brasilia = pytz.timezone("America/Sao_Paulo")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def buscar_jogos():
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    data = []

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params={"next": 10}) as resp:
            result = await resp.json()
            for jogo in result.get("response", []):
                teams = jogo["teams"]
                league = jogo["league"]
                fixture = jogo["fixture"]

                data_jogo = datetime.fromisoformat(fixture["date"].replace("Z", "+00:00")).astimezone(fuso_brasilia)
                jogo_formatado = (
                    f"🏆 {league['name']} ({league['country']})\n"
                    f"📅 {data_jogo.strftime('%d/%m %H:%M')}\n"
                    f"⚽ {teams['home']['name']} x {teams['away']['name']}"
                )
                data.append(jogo_formatado)
    return data

async def enviar_boletim(context: ContextTypes.DEFAULT_TYPE):
    logging.info("Enviando boletim de jogos...")
    jogos = await buscar_jogos()
    if jogos:
        texto = "🔥 *Boletim de Jogos do Dia*\n\n" + "\n\n".join(jogos)
        await context.bot.send_message(chat_id=CANAL_ID, text=texto, parse_mode=ParseMode.MARKDOWN)
    else:
        await context.bot.send_message(chat_id=CANAL_ID, text="Nenhum jogo encontrado.")

async def start_bot():
    application = ApplicationBuilder().token(TOKEN).build()

    scheduler = AsyncIOScheduler(timezone=fuso_brasilia)
    scheduler.add_job(enviar_boletim, "interval", hours=1, next_run_time=datetime.now(fuso_brasilia))
    scheduler.start()

    logging.info("Bot iniciado com Webhook no Render.")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_bot())
