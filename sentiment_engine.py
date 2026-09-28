import sqlite3
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download VADER lexicon (only needed once)
nltk.download('vader_lexicon', quiet=True)

def analyze_sentiment():
    print("🧠 Analyzing News Sentiment...")
    conn = sqlite3.connect('macro_data.db')
    
    # Load news
    news_df = pd.read_sql("SELECT * FROM News_Headlines", conn)
    sia = SentimentIntensityAnalyzer()
    
    scores = []
    for ticker in news_df['Ticker'].unique():
        ticker_news = news_df[news_df['Ticker'] == ticker]['Headline']
        compound_scores = []
        
        for headline in ticker_news:
            score = sia.polarity_scores(str(headline))['compound']
            compound_scores.append(score)
            
        # Average sentiment for the asset
        avg_sentiment = sum(compound_scores) / len(compound_scores) if compound_scores else 0
        scores.append({'Ticker': ticker, 'Sentiment_Score': avg_sentiment})
        
    sentiment_df = pd.DataFrame(scores)
    sentiment_df.to_sql('Sentiment_Scores', conn, if_exists='replace', index=False)
    conn.close()
    print("✅ Sentiment Analysis Complete!")

if __name__ == "__main__":
    analyze_sentiment()