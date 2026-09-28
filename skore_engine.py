import sqlite3
import pandas as pd
import numpy as np

def calculate_skore():
    print("🧠 Calculating SKORE Rankings...")
    conn = sqlite3.connect('macro_data.db')
    
    # 1. Load asset price data
    df = pd.read_sql("SELECT * FROM Assets", conn)
    df.set_index('Date', inplace=True)
    
    scores = []
    for ticker in ['GLD', 'TLT', 'QQQ', 'XLE', 'BTC-USD']:
        if ticker in df.columns:
            prices = df[ticker].dropna()
            momentum = (prices.iloc[-1] / prices.iloc[-90] - 1) if len(prices) > 90 else 0
            volatility = prices.pct_change().tail(90).std() * np.sqrt(252)
            stability = 1 / (1 + volatility)
            scores.append({'Ticker': ticker, 'Momentum': momentum, 'Stability': stability})

    score_df = pd.DataFrame(scores)
    
    # Normalize Momentum & Stability
    score_df['Mom_Score'] = ((score_df['Momentum'] - score_df['Momentum'].min()) / (score_df['Momentum'].max() - score_df['Momentum'].min() + 1e-9)) * 100
    score_df['Stab_Score'] = ((score_df['Stability'] - score_df['Stability'].min()) / (score_df['Stability'].max() - score_df['Stability'].min() + 1e-9)) * 100
    
    # 2. Load Sentiment Data (NEW)
    try:
        sent_df = pd.read_sql("SELECT * FROM Sentiment_Scores", conn)
        score_df = score_df.merge(sent_df, on='Ticker', how='left')
        score_df['Sentiment_Score'] = score_df['Sentiment_Score'].fillna(0)
        # Normalize Sentiment (-1 to 1) -> (0 to 100)
        score_df['Sent_Norm'] = ((score_df['Sentiment_Score'] + 1) / 2) * 100
    except:
        score_df['Sent_Norm'] = 50 # Default if no news

    # Final SKORE: 50% Momentum + 30% Stability + 20% Sentiment
    score_df['SKORE'] = (score_df['Mom_Score'] * 0.5) + (score_df['Stab_Score'] * 0.3) + (score_df['Sent_Norm'] * 0.2)
    score_df['SKORE'] = score_df['SKORE'].round(1)
    score_df = score_df.sort_values('SKORE', ascending=False).reset_index(drop=True)
    
    score_df.to_sql('SKORE_Rankings', conn, if_exists='replace', index=False)
    conn.close()
    print("✅ SKORE Engine Complete!")

if __name__ == "__main__":
    calculate_skore()