import logging
import asyncio
from telegram.ext import ApplicationBuilder, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import os

TOKEN = os.getenv("BOT_TOKEN")
GRUPO_ID = os.getenv("GRUPO_ID")

TEXTOS = [
    "🎯 PALPITE 1: Vitória do Real Madrid\nProbabilidade: 79%",
    "🔥 PALPITE 2: Over 2.5 em PSG x Milan\nProbabilidade: 84%",
    "⚽ PALPITE 3: Ambas marcam em Flamengo x Palmeiras\nProbabilidade: 73%",
    "📊 PALPITE 4: Empate entre Grêmio x São Paulo\nProbabilidade: 62%",
    "💥 PALPITE 5: Over 1.5 em Manchester City x Arsenal\nProbabilidade: 90%"
]

async def enviar_palpites(context: ContextTypes.DEFAULT_TYPE):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    mensagem = f"📢 BILHETE DE PALPITES - {agora}\n\n" + "\n\n".join(TEXTOS)
    await context.bot.send_message(chat_id=GRUPO_ID, text=mensagem)

async def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(enviar_palpites, 'interval', minutes=30, args=[app])
    scheduler.start()

    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
