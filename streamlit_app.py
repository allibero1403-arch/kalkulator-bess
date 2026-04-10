import streamlit as st
import pandas as pd

st.set_page_config(page_title="BESS 10/40 Optimizer", layout="centered")

st.title("🔋 Optymalizator Projektu BESS 10MW/40MWh")
st.markdown("---")

# --- SEKCJA WEJŚCIOWA (Suwaki) ---
with st.sidebar:
    st.header("⚙️ Parametry Projektu")
    capex_eur = st.number_input("CAPEX [EUR]", value=8550000, step=50000)
    kurs_eur = st.slider("Kurs EUR/PLN", 4.00, 4.70, 4.30, step=0.01)
    
    st.subheader("🏦 Bank")
    lewar = st.slider("Lewar (LTV) [%]", 50, 85, 70, step=5)
    wibor = st.slider("WIBOR 3M [%]", 4.00, 8.00, 5.85, step=0.05)
    marza_banku = st.slider("Marża Banku [%]", 1.00, 4.00, 2.50, step=0.10)

st.subheader("📈 Przychody i Operacje")
col_input1, col_input2 = st.columns(2)

with col_input1:
    spread_swap = st.slider("Spread SWAP [PLN/MWh]", 200, 600, 380, step=10)
    opex_mw = st.slider("OPEX [PLN/MW/rok]", 30000, 70000, 45000, step=1000)

with col_input2:
    # Twoje dane z aukcji: 6,130 MW
    moc_rm = st.number_input("Ilość w Rynku Mocy [MW]", value=6.130, step=0.1)
    cena_rm = st.number_input("Cena RM [PLN/kW/rok]", value=244.90, step=1.0)

# --- LOGIKA OBLICZEŃ ---
capex_pln = capex_eur * kurs_eur
kwota_kredytu = capex_pln * (lewar / 100)
oprocentowanie = (wibor + marza_banku) / 100

# PRZYCHODY
p_rynek_mocy = moc_rm * 1000 * cena_rm
p_swap = (40 * 310 * 0.85) * spread_swap
suma_przychodow = p_rynek_mocy + p_swap

# EBITDA
koszty_opex = 10 * opex_mw
ebitda = suma_przychodow - koszty_opex

# DŁUG (10 lat)
n = 10
if oprocentowanie > 0:
    rata_roczna = kwota_kredytu * (oprocentowanie / (1 - (1 + oprocentowanie)**-n))
else:
    rata_roczna = kwota_kredytu / n

dscr = ebitda / rata_roczna if rata_roczna > 0 else 0

# --- WIZUALIZACJA ---
st.markdown("---")
st.header("📊 Wyniki Analizy")

m1, m2, m3 = st.columns(3)
m1.metric("EBITDA Roczna", f"{ebitda:,.0f} PLN")
m2.metric("Roczna Rata", f"{rata_roczna:,.0f} PLN")
m3.metric("Wskaźnik DSCR", f"{dscr:.2f}")

# Wykres Struktury Przychodów
st.subheader("Struktura Przychodów Rocznych")
chart_data = pd.DataFrame({
    "Źródło": ["Rynek Mocy (Gwarantowany)", "SWAP (Arbitraż)"],
    "Wartość [PLN]": [p_rynek_mocy, p_swap]
})
st.bar_chart(chart_data, x="Źródło", y="Wartość [PLN]", color="#1f77b4")

# Status Bankowy
if dscr >= 1.25:
    st.success(f"✅ PROJEKT BANKOWALNY (DSCR {dscr:.2f} > 1.25)")
else:
    st.error(f"❌ DSCR ZA NISKI ({dscr:.2f} < 1.25)")

st.write(f"**Wkład własny (Equity):** {capex_pln - kwota_kredytu:,.0f} PLN")
st.caption("Model uwzględnia 17-letni kontrakt mocowy oraz sprawność magazynu 85%.")
