import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuração de Interface para Celular
st.set_page_config(page_title="Animais & Cia Wealth", layout="centered")

# Estilização para parecer um App Nativo
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    [data-testid="stMetricValue"] { color: #38bdf8; font-size: 1.8rem !important; font-weight: 800; }
    .stNumberInput input { background-color: #1e293b !important; color: white !important; border-radius: 10px; }
    .stButton button { width: 100%; background: linear-gradient(90deg, #38bdf8, #818cf8); border: none; padding: 15px; border-radius: 15px; font-weight: bold; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Wealth Manager")
st.caption("Estratégia ARCA + Barsi • Hospital Animais & Cia")

# --- ÁREA DE EDIÇÃO (INPUTS) ---
with st.expander("📝 Atualizar Saldos Atuais", expanded=False):
    aporte = st.number_input("Aporte do Mês (R$)", value=10000, step=1000)
    c1, c2 = st.columns(2)
    s_acoes = c1.number_input("Ações (Barsi)", value=2500)
    s_fii = c2.number_input("Real Estate", value=2500)
    s_caixa = c1.number_input("Caixa/Hedge", value=2500)
    s_int = c2.number_input("Internacional", value=2500)

# --- CÁLCULOS E LÓGICA ---
total_atual = s_acoes + s_fii + s_caixa + s_int
total_futuro = total_atual + aporte
meta = total_futuro / 4

gaps = {
    "Ações": max(0, meta - s_acoes),
    "Real Estate": max(0, meta - s_fii),
    "Caixa": max(0, meta - s_caixa),
    "Internacional": max(0, meta - s_int)
}
total_gaps = sum(gaps.values())

# --- DASHBOARD VISUAL ---
st.markdown("### Resumo Patrimonial")
m1, m2 = st.columns(2)
m1.metric("Total Atual", f"R$ {total_atual:,.0f}")
m2.metric("Meta p/ Classe", f"R$ {meta:,.0f}")

# Gráfico Interativo
fig = go.Figure(data=[go.Pie(
    labels=list(gaps.keys()), 
    values=[s_acoes, s_fii, s_caixa, s_int], 
    hole=.7,
    marker_colors=['#38bdf8', '#818cf8', '#4ade80', '#fb7185']
)])
fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 🛒 Onde Comprar Hoje")

for classe, gap in gaps.items():
    valor_classe = (gap / total_gaps) * aporte if total_gaps > 0 else aporte / 4
    if valor_classe > 0:
        st.markdown(f"""
        <div style="background:#1e293b; padding:15px; border-radius:15px; margin-bottom:10px; border-left: 5px solid #38bdf8;">
            <p style="margin:0; font-size:0.8rem; opacity:0.6;">{classe}</p>
            <h2 style="margin:0; color:#4ade80;">R$ {valor_classe:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
        if classe == "Ações":
            st.info(f"BBAS3: R$ {valor_classe/3:,.2f} | CPLE6: R$ {valor_classe/3:,.2f} | PSSA3: R$ {valor_classe/3:,.2f}")
        elif classe == "Real Estate":
            st.info(f"ALZR11: R$ {valor_classe/3:,.2f} | XPML11: R$ {valor_classe/3:,.2f} | KNIP11: R$ {valor_classe/3:,.2f}")
