import os
import sqlite3
import pandas as pd
import yfinance as yf
from fredapi import Fred
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

load_dotenv()
FRED_API_KEY = os.getenv('FRED_API_KEY')
fred = Fred(api_key=FRED_API_KEY)

MACRO_SERIES = {'10Y_Yield': 'DGS10', '2Y_Yield': 'DGS2', 'CPI': 'CPIAUCSL', 'M2_Money_Supply': 'WM2NS'}
ASSETS = {'GLD': 'Gold', 'TLT': 'Bonds', 'QQQ': 'Tech', 'XLE': 'Energy', 'BTC-USD': 'Bitcoin'}

def fetch_and_store_data():
    print(" Starting XY Data Pipeline...")
    conn = sqlite3.connect('macro_data.db')
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*2)

    # 1. Macro Data
    for name, series_id in MACRO_SERIES.items():
        try:
            data = fred.get_series(series_id, start_date, end_date).dropna().reset_index()
            data.columns = ['Date', name]
            data['Date'] = pd.to_datetime(data['Date'])
            data.to_sql(name, conn, if_exists='replace', index=False)
        except Exception as e: print(f"Error {name}: {e}")

    # 2. Yield Spread
    try:
        query = "SELECT a.Date, a.[10Y_Yield], b.[2Y_Yield], (a.[10Y_Yield] - b.[2Y_Yield]) as Yield_Spread FROM [10Y_Yield] a JOIN [2Y_Yield] b ON a.Date = b.Date"
        pd.read_sql(query, conn).to_sql('Yield_Spread', conn, if_exists='replace', index=False)
    except: pass

    # 3. Asset Data
    print("Fetching Assets...")
    asset_data = yf.download(list(ASSETS.keys()), start=start_date, end=end_date)['Close']
    asset_data = asset_data.reset_index()
    asset_data.columns = [col[0] if isinstance(col, tuple) else col for col in asset_data.columns]
    asset_data['Date'] = pd.to_datetime(asset_data['Date'])
    asset_data.to_sql('Assets', conn, if_exists='replace', index=False)

            # 4. News Data (FIXED)
    print("Fetching News Headlines...")
    news_list = []
    for ticker in ASSETS.keys():
        try:
            t = yf.Ticker(ticker)
            news = t.news
            if news:
                for item in news[:5]:
                    # Title is nested inside 'content'
                    title = item.get('content', {}).get('title', '')
                    
                    if not title or title.strip() == '':
                        continue
                        
                    news_list.append({'Ticker': ticker, 'Headline': title})
                    print(f"  ✓ {ticker}: {title[:60]}...")
        except Exception as e:
            print(f"News error for {ticker}: {e}")
            
    if news_list:
        news_df = pd.DataFrame(news_list)
        news_df.to_sql('News_Headlines', conn, if_exists='replace', index=False)
        print(f"✅ Stored {len(news_list)} news headlines")
    else:
        print("⚠️ No news headlines captured")

if __name__ == "__main__":
    fetch_and_store_data()