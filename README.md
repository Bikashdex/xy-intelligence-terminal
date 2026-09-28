# 🌐 XY Intelligence Terminal

An AI-powered, real-time financial intelligence platform built to mirror the institutional-grade architecture of **World Trade Factory (SKXYWTF)**. 

## 🚀 Features
- **Macro Pulse**: Real-time tracking of Yield Curve Spread, CPI, and M2 Liquidity via FRED API.
- **SKORE Engine**: Proprietary quantitative scoring (50% Momentum, 30% Stability, 20% News Sentiment).
- **Trade Intelligence**: NLP-driven sentiment analysis (VADER) on live financial news headlines.
- **Agentic AI Advisor**: RAG-powered LLM interface (Gemini) that answers natural language queries using live database context.

## 🛠️ Tech Stack
- **Backend**: Python, SQLite, Pandas, yfinance, FRED API
- **AI/ML**: Google Gemini API, NLTK (VADER Sentiment)
- **Frontend**: Streamlit, Plotly

## 📊 How to Run Locally
1. `pip install -r requirements.txt`
2. Add `FRED_API_KEY` and `GEMINI_API_KEY` to a `.env` file.
3. Run `python pipeline.py`, `python sentiment_engine.py`, `python skore_engine.py`
4. Launch with `streamlit run app.py`