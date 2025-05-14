import discord
import yfinance as yf
import pandas as pd
import numpy as np
import asyncio

TOKEN = "MTM3MjEwMDk3NDk4MTgxMjI3NQ.GBtZ2U.8m0jbeZBREBrmlIBJD1fu-2xbeSxQrAaNvRMqs"
CHANNEL_ID = 1159841547957837877 # ID de ton salon Discord

def compute_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyser(symbole):
    try:
        df = yf.download(symbole, period='1mo', interval='1d')
        df['RSI'] = compute_rsi(df['Close'])
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        dernier = df.iloc[-1]

        signal = "ATTENDRE"
        if dernier['RSI'] < 30 and dernier['MA20'] > dernier['MA50']:
            signal = "ACHETER"
        elif dernier['RSI'] > 70 and dernier['MA20'] < dernier['MA50']:
            signal = "VENDRE"

        return f"{symbole}: {signal} (RSI={dernier['RSI']:.1f}, MME20={dernier['MA20']:.2f}, MME50={dernier['MA50']:.2f})"
    except Exception as e:
        return f"{symbole}: ERREUR ({e})"

class TradingBot(discord.Client):
    async def on_ready(self):
        print(f'Connecté en tant que {self.user}')
        canal = self.get_channel(CHANNEL_ID)

        tickers = ['TTE.PA', 'AIR.PA', 'BNP.PA', 'ORA.PA', 'ENGI.PA', 'SAN.PA', 'VIE.PA']
        messages = [analyser(ticker) for ticker in tickers]
        await canal.send("**Analyse quotidienne du marché :**")
        for msg in messages:
            await canal.send(msg)
        await self.close()

intents = discord.Intents.default()
bot = TradingBot(intents=intents)
bot.run(TOKEN)
