import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
from ai_agent import ask_ai

st.set_page_config(page_title="XY Intelligence Terminal", layout="wide", page_icon="📈")

@st.cache_data(ttl=3600)
def load_data():
    conn = sqlite3.connect('macro_data.db')
    data = {
        'yield': pd.read_sql("SELECT * FROM Yield_Spread", conn),
        'cpi': pd.read_sql("SELECT * FROM CPI", conn),
        'm2': pd.read_sql("SELECT * FROM M2_Money_Supply", conn),
        'sp500': pd.read_sql("SELECT Date, Close FROM SP500", conn),
        'skore': pd.read_sql("SELECT * FROM SKORE_Rankings", conn),
        'news': pd.read_sql("SELECT * FROM News_Headlines", conn),
        'sentiment': pd.read_sql("SELECT * FROM Sentiment_Scores", conn)
    }
    conn.close()
    return data

data = load_data()

st.title("🌐 XY Intelligence Terminal")
st.markdown("Real-time macro, quantitative, trade intelligence, and AI advisory.")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Macro Pulse", "🏆 SKORE Terminal", "🌍 Trade Intelligence", " AI Advisor"])

# --- TAB 1: MACRO ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Yield Curve Spread")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['yield']['Date'], y=data['yield']['Yield_Spread'], line=dict(color='#00ffcc')))
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        fig.update_layout(template="plotly_dark", height=300, margin=dict(t=10, b=0))
        st.plotly_chart(fig, width="stretch")
    with col2:
        st.subheader("S&P 500")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['sp500']['Date'], y=data['sp500']['Close'], line=dict(color='#ff9900')))
        fig.update_layout(template="plotly_dark", height=300, margin=dict(t=10, b=0))
        st.plotly_chart(fig, width="stretch")

# --- TAB 2: SKORE ---
with tab2:
    st.subheader("🏆 Live Asset SKORE Rankings")
    st.markdown("Scoring: 50% Momentum + 30% Stability + 20% News Sentiment")
    skore_df = data['skore']
    st.dataframe(skore_df[['Ticker', 'SKORE', 'Mom_Score', 'Stab_Score', 'Sent_Norm']].style.highlight_max(subset=['SKORE'], color='darkgreen'), use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig_bar = px.bar(skore_df, x='Ticker', y='SKORE', color='SKORE', color_continuous_scale='Viridis', text='SKORE')
        fig_bar.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig_bar, width="stretch")
    with col2:
        skore_df['Allocation'] = (skore_df['SKORE'] / skore_df['SKORE'].sum() * 100).round(1)
        fig_pie = px.pie(skore_df, values='Allocation', names='Ticker', hole=0.4, color_discrete_sequence=px.colors.sequential.Plasma)
        fig_pie.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig_pie, width="stretch")

# --- TAB 3: TRADE INTELLIGENCE ---
with tab3:
    st.subheader(" World Trade Intelligence Feed")
    feed = data['news'].merge(data['sentiment'], on='Ticker')
    
    for index, row in feed.iterrows():
        sentiment = row['Sentiment_Score']
        if sentiment > 0.05:
            emoji = "🟢"
            label = "Positive"
        elif sentiment < -0.05:
            emoji = "🔴"
            label = "Negative"
        else:
            emoji = "⚪"
            label = "Neutral"
            
        st.markdown(f"**{row['Ticker']}** {emoji} *({label}: {sentiment:.2f})*")
        st.markdown(f"> {row['Headline']}")
        st.divider()

# --- TAB 4: AI ADVISOR (NEW) ---
with tab4:
    st.subheader("🤖 AI Wealth Advisor")
    st.markdown("Ask questions about the current market, rankings, or macro conditions.")
    
    # Example questions
    st.markdown("**Try asking:**")
    st.markdown("- *Why is the top-ranked asset performing well?*")
    st.markdown("- *What is the current macro regime?*")
    st.markdown("- *Which assets have the best sentiment?*")
    st.markdown("- *Should I be worried about the yield curve?*")
    
    # Chat input
    user_question = st.text_input("Your question:", placeholder="Ask about markets, rankings, or macro conditions...")
    
    if user_question:
        with st.spinner("Analyzing data and generating insights..."):
            response = ask_ai(user_question)
        
        st.markdown("### 💡 AI Response:")
        st.markdown(response)