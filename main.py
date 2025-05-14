import discord
import yfinance as yf
import pandas as pd
import numpy as np
import asyncio

from dotenv import load_dotenv
import os

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
        # Télécharge les données sur 3 mois, avec un intervalle de 1 jour
        df = yf.download(symbole, period='3mo', interval='1d')
        
        # Si les données sont insuffisantes, on renvoie une erreur
        if df.shape[0] < 20:
            return f"{symbole}: Pas assez de données pour une analyse fiable."
        
        df = df.dropna()  # Supprimer les valeurs manquantes
        df['RSI'] = compute_rsi(df['Close'])
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()

        dernier = df.iloc[-1]

        # Vérifier que les valeurs sont valides avant de faire les calculs
        if np.isnan(dernier['RSI']) or np.isnan(dernier['MA20']) or np.isnan(dernier['MA50']):
            return f"{symbole}: Erreur d'analyse, données invalides."

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

        tickers = [
            'TTE.PA', 'AIR.PA', 'BNP.PA', 'ORA.PA', 'ENGI.PA', 'SAN.PA', 'VIE.PA', 
            'AC.PA', 'MC.PA', 'RNO.PA', 'DG.PA', 'KER.PA', 'GLE.PA', 'PUB.PA',
            'OR.PA', 'FR.PA', 'BN.PA', 'AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA', 
            'META', 'NVDA', 'SPY', 'BRK-B', 'WMT', 'DIS', 'BA', 'GS', 'JPM', 'MA',
            'IBM', 'NFLX'
        ]

        valid_tickers = []

        # Vérification des tickers valides
        for ticker in tickers:
            try:
                # Essaye de télécharger les données du ticker
                yf.download(ticker, period='3mo', interval='1d')
                valid_tickers.append(ticker)  # Si les données sont valides, on les ajoute à la liste
            except Exception as e:
                print(f"Erreur avec {ticker}: {e}")  # Affiche l'erreur et passe au ticker suivant

        print(f"Tickers valides : {valid_tickers}")
        
        messages = [analyser(ticker) for ticker in valid_tickers]
        await canal.send("**Analyse quotidienne du marché :**")
        for msg in messages:
            await canal.send(msg)
        await self.close()

intents = discord.Intents.default()
bot = TradingBot(intents=intents)
bot.run(TOKEN)
