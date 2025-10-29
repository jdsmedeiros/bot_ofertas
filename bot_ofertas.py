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
# FUNÇÕES DE BUSCA DE OFERTAS
# ----------------------------
async def buscar_mercadolivre(session, termo):
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo.replace(' ', '+')}"
    async with session.get(url) as resp:
        data = await resp.json()
        resultados = []
        for item in data.get("results", [])[:3]:  # até 3 ofertas por termo
            resultados.append({
                "titulo": item["title"],
                "preco": f'R${item["price"]:.2f}',
                "imagem": item["thumbnail"].replace("I.jpg", "O.jpg"),
                "link": item["permalink"],
                "site": "Mercado Livre"
            })
        return resultados

async def buscar_amazon(session, termo):
    return [
        {
            "titulo": f"{termo.title()} - Oferta Amazon 🔥",
            "preco": "R$ 5.499,00",
            "imagem": "https://m.media-amazon.com/images/I/61aUBxqc5PL._AC_SL1500_.jpg",
            "link": f"https://www.amazon.com.br/s?k={termo.replace(' ', '+')}",
            "site": "Amazon"
        }
    ]

async def buscar_aliexpress(session, termo):
    url = f"https://m.aliexpress.com/wholesale/{termo.replace(' ', '-')}.html"
    return [
        {
            "titulo": f"{termo.title()} - Promoção AliExpress 💥",
            "preco": "A partir de R$ 299,00",
            "imagem": "https://ae01.alicdn.com/kf/Sa7c3b27f1d6148f2b4c2e2b64a70b0e7M.jpg",
            "link": url,
            "site": "AliExpress"
        }
    ]

async def buscar_shopee(session, termo):
    return [
        {
            "titulo": f"{termo.title()} - Desconto Shopee 🧡",
            "preco": "R$ 279,00",
            "imagem": "https://down-br.img.susercontent.com/file/br-11134207-7r98v-lvjz43er4k7p13",
            "link": f"https://shopee.com.br/search?keyword={termo.replace(' ', '%20')}",
            "site": "Shopee"
        }
    ]

# ----------------------------
# ENVIO DE MENSAGENS TELEGRAM
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

        # Busca todas as ofertas de todos os termos
        for termo in PALAVRAS_CHAVE:
            ofertas = []
            ofertas += await buscar_mercadolivre(session, termo)
            ofertas += await buscar_amazon(session, termo)
            ofertas += await buscar_aliexpress(session, termo)
            ofertas += await buscar_shopee(session, termo)
            todas_ofertas.extend(ofertas)

        # Escolhe aleatoriamente até 4 ofertas diferentes
        if len(todas_ofertas) > 4:
            ofertas_selecionadas = random.sample(todas_ofertas, 4)
        else:
            ofertas_selecionadas = todas_ofertas

        # Envia uma a uma com pequeno intervalo
        for oferta in ofertas_selecionadas:
            await enviar_oferta(bot, oferta)
            await asyncio.sleep(2)

        hora = datetime.now(timezone("America/Sao_Paulo")).strftime("%H:%M")
        print(f"✅ Envio concluído às {hora} (horário de Brasília)")

# ----------------------------
# AGENDAMENTO (3 VEZES AO DIA)
# ----------------------------
async def main():
    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(enviar_ofertas_diarias, "cron", hour=9, minute=0)
    scheduler.add_job(enviar_ofertas_diarias, "cron", hour=15, minute=0)
    scheduler.add_job(enviar_ofertas_diarias, "cron", hour=19, minute=0)
    scheduler.start()

    print("🤖 Bot de ofertas ativo! Envia às 9h, 15h e 19h (horário de Brasília)")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
