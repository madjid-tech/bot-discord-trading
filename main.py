import yfinance as yf
import pandas as pd

# Fonction pour calculer le RSI
def compute_rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

# Liste des actions à analyser
actions = [
    'TTE.PA', 'AIR.PA', 'BNP.PA', 'ORA.PA', 'ENGI.PA', 'SAN.PA', 'VIE.PA', 'AC.PA', 
    'MC.PA', 'RNO.PA', 'DG.PA', 'KER.PA', 'GLE.PA', 'PUB.PA', 'OR.PA', 'FR.PA', 
    'BN.PA', 'AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA', 'META', 'NVDA', 'SPY', 'BRK-B', 
    'WMT', 'DIS', 'BA', 'GS', 'JPM', 'MA', 'IBM', 'NFLX'
]

# Fonction pour analyser une action
def analyser(symbole):
    try:
        # Tentative de téléchargement des données boursières
        df = yf.download(symbole, period='3mo', interval='1d')
        
        # Vérification si les données sont vides
        if df.empty:
            return f"{symbole}: Pas de données disponibles."
        
        # Calcul des indicateurs (RSI, moyennes mobiles)
        df['RSI'] = compute_rsi(df['Close'])
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()

        # Dernière ligne pour analyse
        dernier = df.iloc[-1]
        
        # Vérification si les valeurs nécessaires sont présentes
        if pd.isna(dernier['RSI']) or pd.isna(dernier['MA20']) or pd.isna(dernier['MA50']):
            return f"{symbole}: Pas assez de données pour une analyse fiable."

        # Logique de trading
        signal = "ATTENDRE"
        if dernier['RSI'] < 30 and dernier['MA20'] > dernier['MA50']:
            signal = "ACHETER"
        elif dernier['RSI'] > 70 and dernier['MA20'] < dernier['MA50']:
            signal = "VENDRE"

        return f"{symbole}: {signal} (RSI={dernier['RSI']:.1f}, MME20={dernier['MA20']:.2f}, MME50={dernier['MA50']:.2f})"
    except yf.YFPricesMissingError:
        # En cas d'erreur liée au téléchargement (probablement délisté)
        return f"{symbole}: Action délistée ou données manquantes."
    except Exception as e:
        # Catch toutes les autres erreurs
        return f"{symbole}: ERREUR ({e})"

# Fonction pour analyser plusieurs actions
def analyser_actions(actions):
    results = []
    for action in actions:
        result = analyser(action)
        results.append(result)
    return results

# Exécution et affichage des résultats
if __name__ == "__main__":
    resultats = analyser_actions(actions)
    
    # Affichage des résultats
    for resultat in resultats:
        print(resultat)
