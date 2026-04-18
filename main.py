import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# CONFIGURAÇÃO VISUAL "PLANNER"
st.set_page_config(page_title="Wealth Planner Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #1e293b; }
    .metric-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
    h1, h2, h3 { color: #0f172a; font-weight: 800; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f1f5f9; border-radius: 10px; padding: 10px 20px; color: #64748b; }
    .stTabs [aria-selected="true"] { background-color: #38bdf8 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO PARA PEGAR PREÇOS REAIS ---
@st.cache_data(ttl=600)
def pegar_precos(tickers):
    precos = {}
    for t in tickers:
        try:
            acao = yf.Ticker(t + ".SA")
            precos[t] = acao.history(period="1d")['Close'].iloc[-1]
        except:
            precos[t] = 0.0
    return precos

# ATIVOS DO MARCELO
tickers_acoes = ["BBAS3", "CPLE6", "PSSA3"]
tickers_fiis = ["ALZR11", "XPML11", "KNIP11"]

st.title("🏦 Wealth Planner Pro")
st.caption("Gestão Patrimonial Marcelo Stacciarini • Dados B3 em Tempo Real")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "💎 Carteira B3", "⚙️ Ajustar Aporte"])

# --- TELA 3: CONFIGURAÇÃO (FEITA PRIMEIRO PARA OS CÁLCULOS) ---
with tab3:
    st.subheader("Configurações do Mês")
    aporte = st.number_input("Valor do Aporte Mensal (R$)", value=10000)
    st.info("Insira a quantidade que você possui de cada ativo:")
    col_a, col_b = st.columns(2)
    qtd_bbas = col_a.number_input("Qtd BBAS3", value=100)
    qtd_alzr = col_b.number_input("Qtd ALZR11", value=50)
    # Adicione outros inputs conforme necessário

# BUSCA DE PREÇOS REAIS
precos = pegar_precos(tickers_acoes + tickers_fiis)

# CÁLCULOS
valor_acoes = (precos["BBAS3"] * qtd_bbas) # Exemplo simplificado
valor_fiis = (precos["ALZR11"] * qtd_alzr)
total_patrimonio = valor_acoes + valor_fiis

# --- TELA 1: DASHBOARD ---
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="metric-card"><p style="margin:0;opacity:0.6">Patrimônio Total</p><h2>R$ {total_patrimonio:,.2f}</h2></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><p style="margin:0;opacity:0.6">Aporte Projetado</p><h2 style="color:#38bdf8">R$ {aporte:,.2f}</h2></div>', unsafe_allow_html=True)
    
    # Gráfico Planner
    fig = go.Figure(data=[go.Pie(labels=['Ações', 'FIIs'], values=[valor_acoes, valor_fiis], hole=.6)])
    fig.update_layout(margin=dict(t=20, b=20, l=0, r=0), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

# --- TELA 2: MINHA CARTEIRA (B3 REAL TIME) ---
with tab2:
    st.subheader("Cotações Atualizadas (15min delay)")
    for t in tickers_acoes + tickers_fiis:
        preco_atual = precos.get(t, 0)
        st.write(f"**{t}**: R$ {preco_atual:.2f}")
    
    st.warning("Os dados são puxados automaticamente via Yahoo Finance.")
