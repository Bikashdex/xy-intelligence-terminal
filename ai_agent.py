import os
import sqlite3
import pandas as pd
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize the client
client = genai.Client(api_key=GEMINI_API_KEY)

def get_context():
    conn = sqlite3.connect('macro_data.db')
    skore_df = pd.read_sql("SELECT * FROM SKORE_Rankings ORDER BY SKORE DESC", conn)
    yield_df = pd.read_sql("SELECT * FROM Yield_Spread ORDER BY Date DESC LIMIT 1", conn)
    cpi_df = pd.read_sql("SELECT * FROM CPI ORDER BY Date DESC LIMIT 1", conn)
    m2_df = pd.read_sql("SELECT * FROM M2_Money_Supply ORDER BY Date DESC LIMIT 1", conn)
    sentiment_df = pd.read_sql("SELECT * FROM Sentiment_Scores", conn)
    conn.close()
    
    return f"""
SKORE RANKINGS:
{skore_df[['Ticker', 'SKORE', 'Mom_Score', 'Stab_Score', 'Sent_Norm']].to_string()}

MACRO: Yield Spread: {yield_df['Yield_Spread'].values[0]:.2f}%, CPI: {cpi_df['CPI'].values[0]:.0f}, M2: ${m2_df['M2_Money_Supply'].values[0]/1000:.1f}T
SENTIMENT: {sentiment_df.to_string()}
"""

def ask_ai(question):
    context = get_context()
    prompt = f"""You are an elite AI financial analyst at World Trade Factory (SKXYWTF). 
Use this data to answer: {context}
User Question: {question}
Answer concisely, professionally, and data-driven."""

    try:
        # Using the EXACT model name the API requested in the error message
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print("Testing AI Agent...")
    print("\nAI Response:")
    print(ask_ai("Why is the top-ranked asset performing well?"))