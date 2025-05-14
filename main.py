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
        df = yf.download(symbole, period='3mo', interval='1d')  # 1d pour avoir des données journalières
        if df.empty:
            return f"{symbole}: Pas de données disponibles."
        
        # Calcul RSI et moyennes mobiles
        df['RSI'] = compute_rsi(df['Close'])
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()

        # Récupération des dernières valeurs
        dernier = df.iloc[-1]
        
        # Vérification des valeurs pour éviter les erreurs
        if pd.isna(dernier['RSI']) or pd.isna(dernier['MA20']) or pd.isna(dernier['MA50']):
            return f"{symbole}: Pas assez de données pour une analyse fiable."

        # Logique de trading
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
            'AC.PA', 'LVMH.PA', 'RNO.PA', 'DG.PA', 'KER.PA', 'GLE.PA', 'PUB.PA',
            'EDF.PA', "L'Oreal.PA", 'STMicroelectronics.PA', 'Vinci.PA', 'Dassault.PA',
            'Danone.PA', 'Kering.PA', 'Bouygues.PA', 'Unibail-Rodamco.PA', 'Capgemini.PA',
            'Thales.PA', 'AXA.PA', 'SocieteGenerale.PA', 'Michelin.PA', 'Worldline.PA',
            'Hermes.PA', 'Orange.PA', 'Pernod-Ricard.PA', 'Sodexo.PA', 'Safran.PA',
            'AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA', 'FB', 'SPY', 'NVDA', 'BRK-B', 
            'WMT', 'DIS', 'BA', 'GS', 'JPM', 'MA', 'IBM', 'NFLX', 'NVDA'
        ]
        
        achats = 0
        ventes = 0
        attendre = 0
        
        messages = []
        for ticker in tickers:
            result = analyser(ticker)
            if "ACHETER" in result:
                achats += 1
            elif "VENDRE" in result:
                ventes += 1
            elif "ATTENDRE" in result:
                attendre += 1
            messages.append(result)

        # Envoi des résultats dans le canal Discord
        await canal.send("**Analyse quotidienne du marché :**")
        for msg in messages:
            await canal.send(msg)

        # Envoi du résumé des actions
        await canal.send(f"\n📊 Résumé :\n✅ {achats} actions à acheter\n❌ {ventes} actions à vendre\n🟡 {attendre} actions à garder / attendre")
        await self.close()

intents = discord.Intents.default()
bot = TradingBot(intents=intents)
bot.run(TOKEN)
