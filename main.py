import yfinance as yf
import pandas as pd

def compute_rsi(data, window=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyser(symbole):
    try:
        df = yf.download(symbole, period='3mo', interval='1d')

        if df.empty:
            return f"{symbole}: Pas de données disponibles."

        df['RSI'] = compute_rsi(df['Close'])
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()

        dernier = df.iloc[-1]

        # Vérifie que les valeurs nécessaires sont bien présentes
        if pd.isna(dernier['RSI']) or pd.isna(dernier['MA20']) or pd.isna(dernier['MA50']):
            return f"{symbole}: Pas assez de données pour une analyse fiable."

        # Convertir en float pour éviter l'erreur
        rsi = float(dernier['RSI'])
        ma20 = float(dernier['MA20'])
        ma50 = float(dernier['MA50'])

        signal = "ATTENDRE"
        if rsi < 30 and ma20 > ma50:
            signal = "ACHETER"
        elif rsi > 70 and ma20 < ma50:
            signal = "VENDRE"

        return f"{symbole}: {signal} (RSI={rsi:.1f}, MME20={ma20:.2f}, MME50={ma50:.2f})"

    except Exception as e:
        return f"{symbole}: ERREUR ({e})"

# Liste d’exemples (tu peux remplacer par tes symboles)
symboles = [
    "AAPL", "GOOGL", "MSFT", "TSLA", "AMZN",
    "TTE.PA", "AIR.PA", "SAN.PA", "ORA.PA", "ENGI.PA"
]

# Résultats
a_acheter = []
a_vendre = []
a_garder = []

for symb in symboles:
    resultat = analyser(symb)
    print(resultat)

    if "ACHETER" in resultat:
        a_acheter.append(symb)
    elif "VENDRE" in resultat:
        a_vendre.append(symb)
    elif "ATTENDRE" in resultat:
        a_garder.append(symb)

# Résumé
print("\n📊 Résumé :")
print(f"✅ {len(a_acheter)} actions à acheter")
print(f"❌ {len(a_vendre)} actions à vendre")
print(f"🟡 {len(a_garder)} actions à garder / attendre")
