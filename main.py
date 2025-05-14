import discord
import yfinance as yf
import pandas as pd
import numpy as np
import asyncio
from datetime import datetime, time, timedelta

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = https://discord.com/oauth2/authorize?client_id=1372100974981812275&permissions=2048&integration_type=0&scope=bot

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
        self.bg_task = self.loop.create_task(self.envoi_quotidien())

    async def envoi_quotidien(self):
        await self.wait_until_ready()canal = self.get_channel(CHANNEL_ID)
if canal is None:
    print("❌ Le canal est introuvable. Vérifie que le bot est sur le bon serveur et a accès à ce canal.")
    return

        
        while not self.is_closed():
            now = datetime.now()
            heure_target = datetime.combine(now.date(), time(17, 0))
            if now > heure_target:
                heure_target += timedelta(days=1)
            await asyncio.sleep((heure_target - now).total_seconds())

            tickers = ['TTE.PA', 'AIR.PA', 'BNP.PA', 'ORA.PA', 'ENGI.PA', 'SAN.PA', 'VIE.PA']
            messages = [analyser(ticker) for ticker in tickers]
            await canal.send("**Analyse quotidienne du marché :**")
            for msg in messages:
                await canal.send(msg)

intents = discord.Intents.all()

bot = TradingBot(intents=intents)
bot.run(TOKEN)
