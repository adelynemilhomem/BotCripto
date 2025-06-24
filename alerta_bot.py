time
import ta
from binance.client import Client
from binance.enums import *
from telegram import Bot
import pandas as pd

# CONFIGURAÇÕES
API_KEY = 
'n38vPbLazYP93MfcxKOChqBFUL5O5ZOfGqfJP6sBuASIQpIrCeFGbWICib4bxEaE'
API_SECRET = 
'JtyeM9zLSy8HxVgh4ABA4A5ij347ONyucXxg6gH9ATKol2SgwjNSvEFiGmLmxLSU'
TELEGRAM_TOKEN = '7722408430:AAFmTFOqnJ0GT6l7LruAIZ_ifYHfP6h-mJo'
CHAT_ID = '5121581395'
INTERVAL = '15m'
SYMBOLS = ['BTCUSDT', 'POLUSDT']

client = Client(API_KEY, API_SECRET)
bot = Bot(token=TELEGRAM_TOKEN)

def get_klines(symbol, interval, limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def analisar(df, symbol):
    df['EMA9'] = ta.trend.ema_indicator(df['close'], window=9)
    df['EMA21'] = ta.trend.ema_indicator(df['close'], window=21)
    df['EMA50'] = ta.trend.ema_indicator(df['close'], window=50)
    df['EMA200'] = ta.trend.ema_indicator(df['close'], window=200)
    df['RSI'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    macd = ta.trend.MACD(df['close'])
    df['MACD'] = macd.macd_diff()

    rsi = df['RSI'].iloc[-1]
    macd_val = df['MACD'].iloc[-1]

    condicao_short = (
        df['EMA9'].iloc[-1] < df['EMA21'].iloc[-1] and
        df['close'].iloc[-1] < df['EMA50'].iloc[-1] and
        rsi < 45 and macd_val < 0
    )
    condicao_long = (
        df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1] and
        df['close'].iloc[-1] > df['EMA50'].iloc[-1] and
        rsi > 55 and macd_val > 0
    )
    if condicao_short:
        return f"⚠️ {symbol} sinal de SHORT | RSI: {rsi:.2f} | MACD: {macd_val:.2f}"
    elif condicao_long:
        return f"📈 {symbol} sinal de LONG | RSI: {rsi:.2f} | MACD: {macd_val:.2f}"
    else:
        return None

def main():
    enviados = {s: '' for s in SYMBOLS}
    while True:
        for symbol in SYMBOLS:
            try:
                df = get_klines(symbol, INTERVAL)
                alerta = analisar(df, symbol)
                if alerta and alerta != enviados[symbol]:
                    bot.send_message(chat_id=CHAT_ID, text=alerta)
                    enviados[symbol] = alerta
            except Exception as e:
                print(f"Erro em {symbol}: {e}")
        time.sleep(900)

if __name__ == '__main__':
    main()
