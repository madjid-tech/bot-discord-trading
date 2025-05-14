import discord
import yfinance as yf
import pandas as pd
import numpy as np
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1159841547957837877  # Ton salon Discord

def compute_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyser(symbole):
    try:
        df = yf.download(symbole, period='3mo', interval='1d', progress=False)
        if df.empty or len(df) < 50:
            return f"{symbole}: ERREUR (Pas assez de données)"

        df['RSI'] = compute_rsi(df['Close'])
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        dernier = df.iloc[-1]

        signal = "ATTENDRE"
        if dernier['RSI'] < 30 and dernier['MA20'] > dernier['MA50']:
            signal = "ACHETER"
        elif dernier['RSI'] > 70 and dernier['MA20'] < dernier['MA50']:
            signal = "VENDRE"

        return f"{symbole}: {signal} (RSI={dernier['RSI']:.1f}, MA20={dernier['MA20']:.2f}, MA50={dernier['MA50']:.2f})"
    except Exception as e:
        return f"{symbole}: ERREUR ({e})"

class TradingBot(discord.Client):
    async def on_ready(self):
        print(f'Connecté en tant que {self.user}')
        canal = self.get_channel(CHANNEL_ID)

        tickers = [
            'TTE.PA', 'AIR.PA', 'BNP.PA', 'ORA.PA', 'ENGI.PA', 'SAN.PA', 'VIE.PA',
            'AC.PA', 'MC.PA', 'RNO.PA', 'DG.PA', 'KER.PA', 'GLE.PA', 'PUB.PA',
            'EDF.PA', 'OR.PA', 'STM.PA', 'DG.PA', 'BN.PA', 'BN.PA',
            'EN.PA', 'URW.PA', 'CAP.PA', 'HO.PA', 'AXA.PA', 'GLE.PA', 'ML.PA', 
            'WLN.PA', 'RMS.PA', 'ORA.PA', 'RI.PA', 'SW.PA', 'SAF.PA',
            'AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA', 'META', 'SPY', 'NVDA', 
            'BRK-B', 'WMT', 'DIS', 'BA', 'GS', 'JPM', 'MA', 'IBM', 'NFLX'
        ]

        acheter, vendre, attendre = 0, 0, 0
        messages = []

        for ticker in tickers:
            result = analyser(ticker)
            messages.append(result)

            if "ACHETER" in result:
                acheter += 1
            elif "VENDRE" in result:
                vendre += 1
            elif "ATTENDRE" in result:
                attendre += 1

        await canal.send("📈 **Analyse quotidienne du marché :**")
        for msg in messages:
            await canal.send(msg)

        await canal.send(
            f"📊 **Résumé :**\n"
            f"✅ {acheter} actions à acheter\n"
            f"❌ {vendre} actions à vendre\n"
            f"🟡 {attendre} actions à garder / attendre"
        )

        await self.close()

intents = discord.Intents.default()
bot = TradingBot(intents=intents)
bot.run(TOKEN)
