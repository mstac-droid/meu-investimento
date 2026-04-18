import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

# CONFIGURAÇÃO DE INTERFACE PLANNER PREMIUM
st.set_page_config(page_title="Wealth Planner Pro V6", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .metric-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
    .stTabs [aria-selected="true"] { background-color: #38bdf8 !important; color: white !important; font-weight: bold; }
    .buy-card { background: #f0fdf4; border-left: 5px solid #22c55e; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE DE ATIVOS ---
config = {
    "Ações Brasil": ["BBAS3", "CPLE6", "PSSA3"],
    "Real Estate": ["ALZR11", "XPML11", "KNIP11"],
    "Hedge/Caixa": ["GOLD11", "LFTS11"],
    "Internacional": ["IVVB11", "BDVY39"]
}

@st.cache_data(ttl=600)
def buscar_dados(tickers):
    precos = {}
    dys = {}
    for t in tickers:
        try:
            tk = yf.Ticker(t + ".SA")
            precos[t] = tk.history(period="1d")['Close'].iloc[-1]
            dys[t] = tk.info.get('dividendYield', 0) * 100 if tk.info.get('dividendYield') else 0
        except:
            precos[t], dys[t] = 0.0, 0.0
    return precos, dys

all_tickers = [t for lista in config.values() for t in lista]
precos_b3, dys_b3 = buscar_dados(all_tickers)

st.title("🏦 Wealth Planner Pro V6")
st.caption(f"Gestão Marcelo Stacciarini • {datetime.now().strftime('%d/%m/%Y')}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "💎 Carteira", "🎯 Novo Aporte", "📈 Evolução", "🔄 Radar Fundamentos"])

# --- LÓGICA DE DADOS (SIDEBAR PARA PERSISTÊNCIA) ---
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    aporte_disponivel = st.number_input("Aporte do Mês (R$)", value=0.0)
    
    dados_usuario = []
    for classe, ativos in config.items():
        st.markdown(f"**{classe}**")
        for t in ativos:
            qtd = st.number_input(f"Qtd {t}", value=0, key=f"q_{t}")
            pm = st.number_input(f"PM {t}", value=0.0, key=f"pm_{t}")
            val = qtd * precos_b3.get(t, 0)
            dados_usuario.append({"Classe": classe, "Ticker": t, "Qtd": qtd, "PM": pm, "Valor": val, "DY": dys_b3.get(t, 0)})

df = pd.DataFrame(dados_usuario)
total_atual = df["Valor"].sum()

# --- ABA 4: EVOLUÇÃO (CRONOLOGIA CORRIGIDA) ---
with tab4:
    st.subheader("Histórico de Crescimento")
    st.info("Preencha o saldo total de cada mês para gerar a curva de evolução:")
    
    meses_ordem = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    historico_valores = []
    col_mes1, col_mes2 = st.columns(2)
    
    for i, mes in enumerate(meses_ordem):
        target_col = col_mes1 if i < 6 else col_mes2
        val_mes = target_col.number_input(f"Saldo {mes}/26", value=0.0, key=f"hist_{mes}", step=1000.0)
        if val_mes > 0:
            historico_valores.append({"Mês": mes, "Patrimônio": val_mes, "Ordem": i})
    
    if historico_valores:
        df_hist = pd.DataFrame(historico_valores).sort_values("Ordem")
        fig_ev = go.Figure(data=go.Scatter(
            x=df_hist["Mês"], 
            y=df_hist["Patrimônio"], 
            mode='lines+markers+text',
            text=[f"R$ {v/1000:.1f}k" for v in df_hist["Patrimônio"]],
            textposition="top center",
            line=dict(color='#38bdf8', width=4),
            marker=dict(size=10, color='#1e293b')
        ))
        fig_ev.update_layout(margin=dict(t=30, b=20, l=0, r=0), yaxis_title="Saldo Total (R$)")
        st.plotly_chart(fig_ev, use_container_width=True)

# --- ABA 3: NOVO APORTE (ARCA) ---
with tab3:
    st.subheader("Rebalanceamento Inteligente")
    meta_classe = (total_atual + aporte_disponivel) * 0.25
    
    resumo_classe = df.groupby("Classe")["Valor"].sum()
    gaps = {classe: max(0, meta_classe - resumo_classe.get(classe, 0)) for classe in config.keys()}
    total_gaps = sum(gaps.values())
    
    for classe, gap in gaps.items():
        v_aporte = (gap / total_gaps * aporte_disponivel) if total_gaps > 0 else (aporte_disponivel / 4)
        if v_aporte > 0:
            st.markdown(f'<div class="buy-card"><b>{classe}</b>: Injetar R$ {v_aporte:,.2f}</div>', unsafe_allow_html=True)
            tickers = config[classe]
            v_por_ticker = v_aporte / len(tickers)
            for t in tickers:
                preco = precos_b3.get(t, 1)
                st.write(f"🛒 Comprar **{int(v_por_ticker/preco)}** cotas de **{t}**")

# --- ABA 1, 2 e 5 (RESUMIDAS) ---
with tab1:
    st.columns(2)[0].markdown(f'<div class="metric-card">Patrimônio Atual<br><h2>R$ {total_atual:,.2f}</h2></div>', unsafe_allow_html=True)
    fig_pie = go.Figure(data=[go.Pie(labels=df["Classe"], values=df["Valor"], hole=.6)])
    st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.dataframe(df.style.format({"PM": "{:.2f}", "Valor": "{:.2f}", "DY": "{:.2f}%"}), use_container_width=True)

with tab5:
    st.subheader("Radar de Fundamentos")
    for _, r in df.iterrows():
        if r["DY"] > 8: st.success(f"💎 {r['Ticker']}: DY Alto ({r['DY']:.1f}%)")
        if r["DY"] < 5 and r["Classe"] == "Ações Brasil": st.error(f"⚠️ {r['Ticker']}: DY Baixo ({r['DY']:.1f}%) - Avaliar Troca")
