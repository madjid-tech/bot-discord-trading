import discord
import yfinance as yf
import pandas as pd
import numpy as np
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1159841547957837877

def compute_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyser(symbole):
    try:
        df = yf.download(symbole, period='6mo', interval='1d', progress=False)
        if df.empty or len(df) < 60:
            return (symbole, None, f"{symbole} ❌ Pas assez de données pour une analyse fiable.")

        df['RSI'] = compute_rsi(df['Close'])
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        dernier = df.iloc[-1]

        if np.isnan(dernier['RSI']) or np.isnan(dernier['MA20']) or np.isnan(dernier['MA50']):
            return (symbole, None, f"{symbole} ❌ Données incomplètes pour le calcul.")

        if dernier['RSI'] < 30 and dernier['MA20'] > dernier['MA50']:
            signal = "ACHETER"
            emoji = "✅"
        elif dernier['RSI'] > 70 and dernier['MA20'] < dernier['MA50']:
            signal = "VENDRE"
            emoji = "❌"
        else:
            signal = "ATTENDRE"
            emoji = "🟡"

        message = (
            f"{symbole} : {emoji} **{signal}**\n"
            f"RSI = {dernier['RSI']:.1f}, MA20 = {dernier['MA20']:.2f}, MA50 = {dernier['MA50']:.2f}"
        )
        return (symbole, signal, message)

    except Exception as e:
        return (symbole, None, f"{symbole} ❌ Erreur d'analyse : {e}")

class TradingBot(discord.Client):
    async def on_ready(self):
        print(f'Connecté en tant que {self.user}')
        canal = self.get_channel(CHANNEL_ID)

        tickers = [
            'TTE.PA', 'AIR.PA', 'BNP.PA', 'ORA.PA', 'ENGI.PA', 'SAN.PA', 'VIE.PA',
            'AC.PA', 'MC.PA', 'RNO.PA', 'DG.PA', 'KER.PA', 'GLE.PA', 'PUB.PA',
            'EDF.PA', 'OR.PA', 'STM.PA', 'FR.PA', 'BN.PA',
            'AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA', 'META', 'NVDA', 'SPY', 'BRK-B',
            'WMT', 'DIS', 'BA', 'GS', 'JPM', 'MA', 'IBM', 'NFLX'
        ]

        await canal.send("📊 **Analyse quotidienne du marché boursier**")

        compte = {"ACHETER": 0, "VENDRE": 0, "ATTENDRE": 0}
        for ticker in tickers:
            symbole, signal, message = analyser(ticker)
            if signal in compte:
                compte[signal] += 1
            await canal.send(message)

        await canal.send(
            f"\n📈 **Résumé :**\n"
            f"✅ {compte['ACHETER']} actions à **acheter**\n"
            f"❌ {compte['VENDRE']} actions à **vendre**\n"
            f"🟡 {compte['ATTENDRE']} actions à **garder / attendre**"
        )

        await self.close()

intents = discord.Intents.default()
bot = TradingBot(intents=intents)
bot.run(TOKEN)
