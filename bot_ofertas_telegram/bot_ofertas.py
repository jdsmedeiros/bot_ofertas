import asyncio
import aiohttp
from telegram import Bot
from telegram.constants import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ----------------------------
# CONFIGURAÇÕES
# ----------------------------
TOKEN = "8398854819:AAHGCzNKqDt0arAx6Fipx2ATbYwtZSA-eLU"
CHAT_ID = "89415579"
PALAVRAS_CHAVE = ["iphone 15 pro", "ssd", "mac mini m4"]

# ----------------------------
# FUNÇÕES DE BUSCA DE OFERTAS
# ----------------------------

async def buscar_mercadolivre(session, termo):
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={termo.replace(' ', '+')}"
    async with session.get(url) as resp:
        data = await resp.json()
        resultados = []
        for item in data.get("results", [])[:2]:  # pega só 2 ofertas por termo
            resultados.append({
                "titulo": item["title"],
                "preco": f'R${item["price"]:.2f}',
                "imagem": item["thumbnail"].replace("I.jpg", "O.jpg"),
                "link": item["permalink"],
                "site": "Mercado Livre"
            })
        return resultados

async def buscar_amazon(session, termo):
    return [{
        "titulo": f"{termo.title()} - Oferta Amazon",
        "preco": "R$ ----",
        "imagem": "https://m.media-amazon.com/images/I/61aUBxqc5PL._AC_SL1500_.jpg",
        "link": "https://www.amazon.com.br/",
        "site": "Amazon"
    }]

async def buscar_aliexpress(session, termo):
    url = f"https://m.aliexpress.com/wholesale/{termo.replace(' ', '-')}.html"
    return [{
        "titulo": f"{termo.title()} - Promoção AliExpress",
        "preco": "A partir de R$ ---",
        "imagem": "https://ae01.alicdn.com/kf/Sa7c3b27f1d6148f2b4c2e2b64a70b0e7M.jpg",
        "link": url,
        "site": "AliExpress"
    }]

async def buscar_shopee(session, termo):
    return [{
        "titulo": f"{termo.title()} - Desconto Shopee",
        "preco": "R$ ---",
        "imagem": "https://down-br.img.susercontent.com/file/br-11134207-7r98v-lvjz43er4k7p13",
        "link": "https://shopee.com.br/",
        "site": "Shopee"
    }]

# ----------------------------
# ENVIO DE MENSAGENS TELEGRAM
# ----------------------------
async def enviar_oferta(bot, oferta):
    mensagem = f"""👌 {oferta['titulo']}
💸 Valor: {oferta['preco']}
🛒 [{oferta['site']}]({oferta['link']})
"""
    await bot.send_photo(
        chat_id=CHAT_ID,
        photo=oferta["imagem"],
        caption=mensagem,
        parse_mode=ParseMode.MARKDOWN
    )

# ----------------------------
# LOOP PRINCIPAL DIÁRIO
# ----------------------------
async def enviar_ofertas_diarias():
    bot = Bot(token=TOKEN)
    async with aiohttp.ClientSession() as session:
        for termo in PALAVRAS_CHAVE:
            ofertas = []
            ofertas += await buscar_mercadolivre(session, termo)
            ofertas += await buscar_amazon(session, termo)
            ofertas += await buscar_aliexpress(session, termo)
            ofertas += await buscar_shopee(session, termo)

            for oferta in ofertas:
                await enviar_oferta(bot, oferta)
                await asyncio.sleep(2)

# ----------------------------
# AGENDAMENTO DIÁRIO
# ----------------------------
async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(enviar_ofertas_diarias, "cron", hour=9, minute=0)  # envia todo dia às 9h
    scheduler.start()

    print("🤖 Bot de ofertas 24h rodando online...")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
