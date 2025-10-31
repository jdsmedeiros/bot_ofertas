import asyncio
import aiohttp
import random
from telegram import Bot
from telegram.constants import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from pytz import timezone

# ----------------------------
# CONFIGURAÇÕES
# ----------------------------
TOKEN = "8398854819:AAHGCzNKqDt0arAx6Fipx2ATbYwtZSA-eLU"
CHAT_ID = "89415579"
PALAVRAS_CHAVE = ["iphone 15 pro", "ssd", "mac mini m4", "monitor gamer", "cadeira gamer"]

# ----------------------------
# BUSCA DE OFERTAS REAIS (Mercado Livre)
# ----------------------------
async def buscar_mercadolivre(session, termo):
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo.replace(' ', '+')}"
    async with session.get(url) as resp:
        data = await resp.json()
        resultados = []
        for item in data.get("results", [])[:3]:
            resultados.append({
                "titulo": item["title"],
                "preco": f'R${item["price"]:.2f}',
                "imagem": item["thumbnail"].replace("I.jpg", "O.jpg"),
                "link": item["permalink"],
                "site": "Mercado Livre"
            })
        return resultados
        print(resultados)

# ----------------------------
# ENVIO TELEGRAM
# ----------------------------
async def enviar_oferta(bot, oferta):
    mensagem = f"""💥 *{oferta['titulo']}*
💸 Valor: {oferta['preco']}
🛒 [{oferta['site']}]({oferta['link']})
"""
    try:
        await bot.send_photo(
            chat_id=CHAT_ID,
            photo=oferta["imagem"],
            caption=mensagem,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"⚠️ Erro ao enviar oferta: {e}")

# ----------------------------
# LOOP PRINCIPAL
# ----------------------------
async def enviar_ofertas_diarias():
    bot = Bot(token=TOKEN)
    async with aiohttp.ClientSession() as session:
        todas_ofertas = []

        # Busca produtos reais de cada termo
        for termo in PALAVRAS_CHAVE:
            ofertas = await buscar_mercadolivre(session, termo)
            todas_ofertas.extend(ofertas)

        # Seleciona 4 ofertas aleatórias entre todos os produtos
        if len(todas_ofertas) > 4:
            ofertas_selecionadas = random.sample(todas_ofertas, 4)
        else:
            ofertas_selecionadas = todas_ofertas

        for oferta in ofertas_selecionadas:
            await enviar_oferta(bot, oferta)
            await asyncio.sleep(2)

        hora = datetime.now(timezone("America/Sao_Paulo")).strftime("%H:%M")
        print(f"✅ Envio concluído às {hora} (horário de Brasília)")

# ----------------------------
# AGENDAMENTO 3x POR DIA
# ----------------------------
async def main():
    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(enviar_ofertas_diarias, "cron", hour=7, minute=0)
    scheduler.add_job(enviar_ofertas_diarias, "cron", hour=10, minute=0)
    scheduler.add_job(enviar_ofertas_diarias, "cron", hour=19, minute=0)
    scheduler.start()

    print("🤖 Bot de ofertas rodando (Brasília): 9h, 15h, 19h")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())

