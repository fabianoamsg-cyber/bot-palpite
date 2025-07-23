import logging
import asyncio
from telegram import Bot
from telegram.ext import ApplicationBuilder, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import os

TOKEN = os.getenv("BOT_TOKEN")
CANAL_ID = os.getenv("GRUPO_ID")

TEXTOS = [
    "🔥 PALPITE 1: Over 2.5 em Real Madrid x Barcelona\nProbabilidade: 78%",
    "⚽ PALPITE 2: Ambas marcam em PSG x Milan\nProbabilidade: 82%",
    "📈 PALPITE 3: Vitória do City contra o Arsenal\nProbabilidade: 71%",
    "🎯 PALPITE 4: Over 1.5 em Flamengo x Palmeiras\nProbabilidade: 85%",
    "💡 PALPITE 5: Empate entre Santos x Vasco\nProbabilidade: 65%"
]

# Envia os palpites no canal
async def enviar_palpites(context: ContextTypes.DEFAULT_TYPE):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    mensagem = f"📊 BILHETE DE PALPITES - {agora}\n\n" + "\n\n".join(TEXTOS)
    await context.bot.send_message(chat_id=CANAL_ID, text=mensagem)

async def main():
    logging.basicConfig(level=logging.INFO)
    application = ApplicationBuilder().token(TOKEN).build()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(enviar_palpites, 'interval', minutes=30, args=[application])
    scheduler.start()

    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
