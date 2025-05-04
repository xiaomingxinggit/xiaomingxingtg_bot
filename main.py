import asyncio
from telegram.ext import ApplicationBuilder
import requests
import os
import logging

# 日志配置
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 从环境变量读取敏感信息
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# OKX API URL
OKX_API_URL = "https://www.okx.com/api/v5/market/tickers?instType=SWAP"

# 要监控的币种
WATCHLIST = ["BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP"]

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

async def send_message():
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

        # 创建并启动应用
        application = ApplicationBuilder().token(TOKEN).build()
        await application.initialize()
        await application.start()  # 启动应用

        # 发送消息
        await application.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")

        # 停止应用
        await application.stop()
        await application.shutdown()  # 清理资源
        logging.info("✅ 消息已成功发送并完成退出。")
    else:
        logging.warning("❌ 获取币价失败或无数据，请检查网络或 API 状态。")

if __name__ == "__main__":
    asyncio.run(send_message())