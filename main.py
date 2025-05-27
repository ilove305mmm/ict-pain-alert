import requests
import time
from binance.client import Client
from config import SYMBOLS, INTERVAL, VOLUME_MULTIPLIER, PRICE_CHANGE_THRESHOLD, HOLD_PERIOD, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

client = Client()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

def fetch_klines(symbol, interval, limit=100):
    return client.get_klines(symbol=symbol, interval=interval, limit=limit)

def analyze(symbol):
    klines = fetch_klines(symbol, INTERVAL)
    closes = [float(k[4]) for k in klines]
    volumes = [float(k[5]) for k in klines]

    avg_vol = sum(volumes[:-1]) / (len(volumes) - 1)
    latest_vol = volumes[-1]
    price_change = (closes[-1] - closes[-2]) / closes[-2] * 100

    if latest_vol > avg_vol * VOLUME_MULTIPLIER:
        if price_change > PRICE_CHANGE_THRESHOLD:
            msg = f"📈 [Max Pain 多單訊號]\n幣種：{symbol}\n成交量激增：{latest_vol:.2f} > {avg_vol:.2f}\n價格變動：+{price_change:.2f}%\n時間：{time.strftime('%Y-%m-%d %H:%M')}"
            send_telegram_message(msg)
        elif price_change < -PRICE_CHANGE_THRESHOLD:
            msg = f"📉 [Max Pain 空單訊號]\n幣種：{symbol}\n成交量激增：{latest_vol:.2f} > {avg_vol:.2f}\n價格變動：{price_change:.2f}%\n時間：{time.strftime('%Y-%m-%d %H:%M')}"
            send_telegram_message(msg)

if __name__ == "__main__":
    while True:
        for sym in SYMBOLS:
            try:
                analyze(sym)
            except Exception as e:
                print(f"Error analyzing {sym}: {e}")
        time.sleep(60)