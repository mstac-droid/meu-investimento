import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# CONFIGURAÇÃO DE INTERFACE
st.set_page_config(page_title="Wealth Planner Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .metric-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
    .stTabs [aria-selected="true"] { background-color: #38bdf8 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE DE ATIVOS (ARCA + BARSI) ---
ativos_config = {
    "Ações Brasil": ["BBAS3", "CPLE6", "PSSA3"],
    "Real Estate": ["ALZR11", "XPML11", "KNIP11"],
    "Hedge/Caixa": ["GOLD11", "LFTS11"],
    "Internacional": ["IVVB11", "BDVY39"]
}

all_tickers = [t + ".SA" for lista in ativos_config.values() for t in lista]

@st.cache_data(ttl=600)
def buscar_cotacoes(tickers):
    try:
        data = yf.download(tickers, period="1d")['Close']
        return data.iloc[-1]
    except:
        return pd.Series()

cotacoes = buscar_cotacoes(all_tickers)

st.title("🏦 Wealth Planner Pro")
st.caption("Gestão Patrimonial Marcelo Stacciarini • V4 Evolução")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "💎 Minha Carteira", "📈 Evolução", "⚙️ Configurar Aportes"])

# --- ABA 4: CONFIGURAÇÃO (DADOS ZERADOS) ---
with tab4:
    st.subheader("Configurações Iniciais")
    aporte_mensal = st.number_input("Valor do Aporte do Mês (R$)", value=0.0)
    
    st.markdown("---")
    st.write("Insira seus dados para cálculo de Preço Médio e DY:")
    
    user_data = []
    for classe, ativos in ativos_config.items():
        st.markdown(f"**{classe}**")
        cols = st.columns(4)
        for t in ativos:
            qtd = cols[0].number_input(f"Qtd {t}", value=0, key=f"q_{t}")
            pm = cols[1].number_input(f"Preço Médio {t}", value=0.0, key=f"pm_{t}")
            dy = cols[2].number_input(f"DY Médio % {t}", value=0.0, key=f"dy_{t}")
            preco_atual = cotacoes.get(t + ".SA", 0.0)
            user_data.append({
                "Classe": classe, "Ticker": t, "Qtd": qtd, "PM": pm, 
                "DY_Medio": dy, "Preco_Atual": preco_atual, "Total": qtd * preco_atual
            })

df_carteira = pd.DataFrame(user_data)
total_patrimonio = df_carteira["Total"].sum()

# --- ABA 1: DASHBOARD ---
with tab1:
    c1, c2 = st.columns(2)
    c1.markdown(f'<div class="metric-card"><p style="margin:0;opacity:0.6">Patrimônio Total</p><h2>R$ {total_patrimonio:,.2f}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><p style="margin:0;opacity:0.6">Aporte do Mês</p><h2 style="color:#38bdf8">R$ {aporte_mensal:,.2f}</h2></div>', unsafe_allow_html=True)
    
    if total_patrimonio > 0:
        resumo = df_carteira.groupby("Classe")["Total"].sum()
        fig = go.Figure(data=[go.Pie(labels=resumo.index, values=resumo.values, hole=.6)])
        st.plotly_chart(fig, use_container_width=True)

# --- ABA 2: MINHA CARTEIRA (DETALHADA) ---
with tab2:
    st.subheader("Análise de Ativos")
    # Tabela formatada
    display_df = df_carteira.copy()
    display_df["Lucro/Prejuízo %"] = ((display_df["Preco_Atual"] / display_df["PM"]) - 1) * 100
    display_df["Lucro/Prejuízo %"] = display_df["Lucro/Prejuízo %"].fillna(0)
    
    st.dataframe(display_df.style.format({
        "PM": "R$ {:.2f}", "Preco_Atual": "R$ {:.2f}", 
        "Total": "R$ {:.2f}", "DY_Medio": "{:.2f}%", "Lucro/Prejuízo %": "{:.2f}%"
    }), use_container_width=True)

# --- ABA 3: EVOLUÇÃO ---
with tab3:
    st.subheader("Evolução do Patrimônio")
    st.info("Insira o valor total da sua carteira no fechamento de cada mês:")
    
    ev_cols = st.columns(3)
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
    historico = []
    for i, mes in enumerate(meses):
        val = ev_cols[i % 3].number_input(f"Saldo {mes}/26 (R$)", value=0.0, key=f"hist_{mes}")
        if val > 0: historico.append({"Mês": mes, "Patrimônio": val})
    
    if historico:
        df_hist = pd.DataFrame(historico)
        fig_ev = go.Figure(data=go.Scatter(x=df_hist["Mês"], y=df_hist["Patrimônio"], mode='lines+markers', line=dict(color='#38bdf8', width=4)))
        fig_ev.update_layout(yaxis_title="R$ Total", margin=dict(t=20, b=20, l=0, r=0))
        st.plotly_chart(fig_ev, use_container_width=True)
