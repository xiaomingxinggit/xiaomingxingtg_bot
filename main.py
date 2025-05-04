from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import logging
import asyncio
from datetime import datetime

# 日志配置
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# OKX API URL
OKX_API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

# 要监控的币种
WATCHLIST = ["BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi，我是行情推送机器人！")

# 获取 OKX 最新价格
def get_okx_latest_price(symbol):
    try:
        resp = requests.get(OKX_API_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") != "0":
            return None

        tickers = data.get("data", [])
        for ticker in tickers:
            if ticker.get("instId") == symbol:
                return ticker.get("last")
    except Exception as e:
        logging.error(f"Error fetching price for {symbol}: {e}")
    return None

# 定时任务：每 5 秒推送一次价格
async def send_prices(context: ContextTypes.DEFAULT_TYPE):
    prices = {}
    for symbol in WATCHLIST:
        price = get_okx_latest_price(symbol)
        if price is not None:
            coin_name = symbol.split("-")[0]
            prices[coin_name] = price

    if prices:
        msg = f"<b>【OKX 最新价格】</b>\n\n"
        for coin, price in prices.items():
            msg += f"{coin}: <code>{price} USDT</code>\n"
        await context.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")

# Bot 启动后自动添加定时任务
async def post_init(application):
    job_queue = application.job_queue
    job_queue.run_repeating(send_prices, interval=5, first=1, name=str(CHAT_ID))
    logging.info("✅ 定时任务已启动，每 5 秒推送一次价格。")

# 启动 Bot
def main():
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)  # Bot 初始化完成后执行
        .build()
    )

    # 可选：添加 /info 命令用于调试
    from telegram.ext import CommandHandler

    async def get_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat_id = user.id
        await update.message.reply_text(f"您的 chat_id 是：<b>{chat_id}</b>", parse_mode="HTML")

    application.add_handler(CommandHandler("info", get_info))

    print("Bot 已启动，将定时推送 OKX 行情...")
    application.run_polling()

if __name__ == "__main__":
    main()