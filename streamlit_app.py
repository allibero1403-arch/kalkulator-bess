import streamlit as st
import pandas as pd
import numpy_financial as npf

# Ustawienie strony
st.set_page_config(page_title="BESS 10MW/40MWh Analysis", layout="centered")

# --- STYLIZACJA CSS DLA SUBTELNYCH NAGŁÓWKÓW ---
st.markdown("""
    <style>
    h3 {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: #444 !important;
        margin-bottom: 0.5rem !important;
        padding-top: 1rem !important;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_box_enabled=True)

st.title("🔋 Kalkulator Inwestycyjny BESS 10/40")
st.markdown("---")

# --- BLOK 1: NAKŁADY INWESTYCYJNE ---
st.subheader("### 1. Nakłady inwestycyjne (CAPEX)")
c1, c2 = st.columns(2)
with c1:
    capex_eur = st.number_input("CAPEX [EUR]", value=8550000, step=50000)
with c2:
    kurs_eur = st.slider("Kurs EUR/PLN", 4.00, 4.70, 4.30, step=0.01)

capex_pln = capex_eur * kurs_eur
st.caption(f"Łączny CAPEX: {capex_pln:,.0f} PLN")

# --- BLOK 2: FINANSOWANIE BANKOWE ---
st.subheader("### 2. Finansowanie bankowe")
b1, b2, b3 = st.columns(3)
with b1:
    lewar = st.slider("Lewar (LTV) [%]", 50, 85, 70, step=5)
with b2:
    wibor = st.slider("WIBOR 3M [%]", 4.00, 8.00, 5.85, step=0.05)
with b3:
    marza = st.slider("Marża Banku [%]", 1.00, 4.00, 2.50, step=0.10)

# --- BLOK 3: KOSZTY OPERACYJNE (OPEX) ---
st.subheader("### 3. Koszty operacyjne (OPEX)")
o1, o2 = st.columns([2, 1])
with o1:
    opex_mw = st.slider("Koszt OPEX [PLN/MW/rok]", 30000, 70000, 45000, step=1000)
with o2:
    st.info(f"Suma OPEX: {10 * opex_mw:,.0f} PLN/rok")

# --- BLOK 4: PRZYCHODY ---
st.subheader("### 4. Strumienie przychodów")
r1, r2 = st.columns(2)
with r1:
    st.markdown("**Rynek Mocy (PSE)**")
    moc_rm = st.number_input("Obowiązek [MW]", value=6.130, step=0.001, format="%.3f")
    cena_rm = st.number_input("Cena [PLN/kW/rok]", value=244.90, step=0.1)
    p_rm = moc_rm * 1000 * cena_rm
with r2:
    st.markdown("**Arbitraż (SWAP)**")
    spread_swap = st.slider("Spread [PLN/MWh]", 200, 600, 380, step=10)
    p_swap = (40 * 310 * 0.85) * spread_swap

# Podsumowanie przychodów i subtelny wykres
suma_p = p_rm + p_swap
st.markdown(f"**Suma przychodów:** {suma_p:,.0f} PLN")

chart_data = pd.DataFrame({
    "Źródło": ["Rynek Mocy", "SWAP"],
    "PLN": [float(p_rm), float(p_swap)]
})
st.bar_chart(chart_data, x="Źródło", y="PLN", color="#A9A9A9", height=200)

# --- LOGIKA FINANSOWA ---
kwota_kredytu = capex_pln * (lewar / 100)
equity = capex_pln - kwota_kredytu
oprocentowanie = (wibor + marza) / 100
ebitda = suma_p - (10 * opex_mw)

# Rata kredytu (10 lat)
n_lat = 10
if oprocentowanie > 0:
    rata = kwota_kredytu * (oprocentowanie / (1 - (1 + oprocentowanie)**-n_lat))
else:
    rata = kwota_kredytu / n_lat

dscr = ebitda / rata if rata > 0 else 0

# Wyliczenie IRR (uproszczone na 15 lat)
# Cash flow: -Wkład własny, potem roczne EBITDA - Rata (przez 10 lat), potem EBITDA (kolejne 5 lat)
cf = [-equity] + [ebitda - rata] * 10 + [ebitda] * 5
irr = npf.irr(cf)

# --- BLOK 5: WYNIKI I RENTOWNOŚĆ ---
st.markdown("---")
st.subheader("### 5. Wyniki i rentowność projektu")
m1, m2, m3 = st.columns(3)
m1.metric("EBITDA", f"{ebitda:,.0f} PLN")
m2.metric("Wskaźnik DSCR", f"{dscr:.2f}")
m3.metric("IRR (15 lat)", f"{irr*100:.2f}%" if not pd.isna(irr) else "N/A")

if dscr >= 1.25:
    st.success(f"Projekt bankowalny (DSCR > 1.25)")
else:
    st.error(f"DSCR poniżej wymogów banku")

st.caption("Kalkulator BESS 10/40 | Model uwzględnia 17-letni kontrakt mocowy.")
