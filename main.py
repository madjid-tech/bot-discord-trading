import discord
import yfinance as yf
import pandas as pd
import numpy as np
import asyncio
from dotenv import load_dotenv
import os

# Chargement du token depuis le fichier .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ID du salon Discord (clic droit > copier l'identifiant)
CHANNEL_ID = 1159841547957837877

# Fonction pour calculer le RSI
def compute_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Fonction d’analyse pour un symbole
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

# Classe du bot Discord
class TradingBot(discord.Client):
    async def on_ready(self):
        print(f'✅ Connecté en tant que {self.user}')
        await self.wait_until_ready()

        canal = self.get_channel(CHANNEL_ID)
        if canal is None:
            print("❌ Le canal est introuvable. Vérifie l'ID du salon et les permissions du bot.")
            return

        tickers = ['TTE.PA', 'AIR.PA', 'BNP.PA', 'ORA.PA', 'ENGI.PA', 'SAN.PA', 'VIE.PA']
        messages = [analyser(ticker) for ticker in tickers]

        await canal.send("**📊 Analyse quotidienne du marché :**")
        for msg in messages:
            await canal.send(msg)

        await self.close()

# Initialisation du bot avec les intents
intents = discord.Intents.default()
bot = TradingBot(intents=intents)

# Lancement du bot
bot.run(TOKEN)
