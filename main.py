import discord
import yfinance as yf
import pandas as pd
import numpy as np
import asyncio
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()  # Charge les variables du fichier .env
TOKEN = os.getenv("DISCORD_TOKEN")

CHANNEL_ID = 1159841547957837877  # ID de ton salon Discord

def compute_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyser(symbole):
    try:
        df = yf.download(symbole, period='1mo', interval='1d')
        
        # Vérifier si les données sont suffisantes
        if df.empty or len(df) < 30:  # Minimum pour calculer RSI, MME20, MME50
            return f"{symbole}: Pas assez de données pour l'analyse."

        df['RSI'] = compute_rsi(df['Close'])
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        dernier = df.iloc[-1]

        # Vérifier si une des colonnes contient des valeurs NaN
        if pd.isna(dernier['RSI']) or pd.isna(dernier['MA20']) or pd.isna(dernier['MA50']):
            return f"{symbole}: Pas assez de données pour l'analyse."

        # Définir le signal d'achat ou de vente
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

        # Liste des symboles à analyser
        tickers = ['TTE.PA', 'AIR.PA', 'BNP.PA', 'ORA.PA', 'ENGI.PA', 'SAN.PA', 'VIE.PA']
        messages = [analyser(ticker) for ticker in tickers]
        
        # Envoi du message d'analyse sur le canal
        await canal.send("**Analyse quotidienne du marché :**")
        for msg in messages:
            await canal.send(msg)

        await self.close()

# Intents par défaut (sans privilèges)
intents = discord.Intents.default()
bot = TradingBot(intents=intents)

# Lancer le bot Discord
bot.run(TOKEN)
