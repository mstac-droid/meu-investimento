import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# CONFIGURAÇÃO DE INTERFACE PREMIUM
st.set_page_config(page_title="Animais & Cia Wealth Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .metric-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 10px; }
    h1, h2, h3 { color: #0f172a; font-weight: 800; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #f1f5f9; border-radius: 10px; padding: 8px 16px; font-size: 0.9rem; }
    .stTabs [aria-selected="true"] { background-color: #38bdf8 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS DE ATIVOS ---
classes = {
    "Ações Brasil": ["BBAS3", "CPLE6", "PSSA3"],
    "Real Estate (FII)": ["ALZR11", "XPML11", "KNIP11"],
    "Caixa/Hedge": ["GOLD11", "LFTS11"],
    "Internacional": ["IVVB11", "BDVY39"]
}

all_tickers = [t + ".SA" for lista in classes.values() for t in lista]

@st.cache_data(ttl=600)
def buscar_cotacoes(tickers):
    data = yf.download(tickers, period="1d")['Close']
    return data.iloc[-1] if not data.empty else pd.Series()

cotacoes = buscar_cotacoes(all_tickers)

# --- INTERFACE ---
st.title("🏦 Wealth Planner Pro")
st.caption("Estratégia ARCA + Barsi • Monitoramento em Tempo Real")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🛒 Ordens de Aporte", "⚙️ Ajustar Quantidades"])

# --- ABA 3: ENTRADA DE DADOS ---
with tab3:
    st.subheader("Configurações de Carteira")
    aporte_mensal = st.number_input("Valor do Novo Aporte (R$)", value=10000)
    
    st.info("Insira quantas cotas/ações você possui atualmente:")
    col1, col2 = st.columns(2)
    
    quantidades = {}
    for i, (classe, ativos) in enumerate(classes.items()):
        target_col = col1 if i % 2 == 0 else col2
        target_col.markdown(f"**{classe}**")
        for ativo in ativos:
            quantidades[ativo] = target_col.number_input(f"Qtd {ativo}", value=1, key=ativo)

# --- PROCESSAMENTO DE VALORES ---
posicao_atual = {}
resumo_classes = {}

for classe, ativos in classes.items():
    soma_classe = 0
    for ativo in ativos:
        preco = cotacoes.get(ativo + ".SA", 0)
        valor_ativo = preco * quantidades[ativo]
        posicao_atual[ativo] = valor_ativo
        soma_classe += valor_ativo
    resumo_classes[classe] = soma_classe

total_patrimonio = sum(resumo_classes.values())
total_com_aporte = total_patrimonio + aporte_mensal
meta_classe = total_com_aporte * 0.25

# --- ABA 1: DASHBOARD ---
with tab1:
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="metric-card"><p style="margin:0;opacity:0.6">Patrimônio Total</p><h2>R$ {total_patrimonio:,.2f}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><p style="margin:0;opacity:0.6">Aporte do Mês</p><h2 style="color:#38bdf8">R$ {aporte_mensal:,.2f}</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card"><p style="margin:0;opacity:0.6">Meta p/ Classe</p><h2>R$ {meta_classe:,.2f}</h2></div>', unsafe_allow_html=True)

    fig = go.Figure(data=[go.Pie(
        labels=list(resumo_classes.keys()), 
        values=list(resumo_classes.values()), 
        hole=.6,
        marker=dict(colors=['#38bdf8', '#818cf8', '#4ade80', '#fb7185'])
    )])
    fig.update_layout(margin=dict(t=30, b=0, l=0, r=0), showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)

# --- ABA 2: ORDENS DE COMPRA ---
with tab2:
    st.subheader("Onde Investir Agora")
    
    gaps = {classe: max(0, meta_classe - valor) for classe, valor in resumo_classes.items()}
    total_gaps = sum(gaps.values())

    for classe, gap in gaps.items():
        valor_destino = (gap / total_gaps * aporte_mensal) if total_gaps > 0 else (aporte_mensal / 4)
        
        if valor_destino > 0:
            with st.container():
                st.markdown(f"""
                <div style="background:white; padding:15px; border-radius:15px; margin-bottom:10px; border-left: 5px solid #38bdf8; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <p style="margin:0; font-size:0.8rem; opacity:0.6;">{classe}</p>
                    <h2 style="margin:0; color:#0f172a;">R$ {valor_destino:,.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Divisão por Tickers
                tickers_da_classe = classes[classe]
                valor_por_ticker = valor_destino / len(tickers_da_classe)
                
                cols = st.columns(len(tickers_da_classe))
                for idx, ticker in enumerate(tickers_da_classe):
                    cols[idx].caption(f"Comprar {ticker}")
                    cols[idx].write(f"**R$ {valor_por_ticker:,.2f}**")
