import streamlit as st

st.set_page_config(page_title="BESS Kalkulator", layout="centered")
st.title("🛠️ Konfiguracja Modelu BESS 10/40")

# Sekcja suwaków
capex = st.slider("CAPEX EUR", 7000000, 10000000, 8550000, step=50000)
kurs = st.slider("Kurs EUR/PLN", 4.0, 4.7, 4.30, step=0.01)
spread = st.slider("Spread SWAP [PLN/MWh]", 200, 600, 380, step=10)
lewar = st.slider("Lewar (LTV) [%]", 50, 85, 70, step=5)

# Obliczenia na żywo
rm_pln = 6.13 * 1000 * 244.90
swap_pln = (40 * 310 * 0.85) * spread
ebitda = (rm_pln + swap_pln) - (10 * 45000)

st.divider()
st.metric("Roczna EBITDA [PLN]", f"{ebitda:,.0f} zł")

if ebitda > 4000000:
    st.success("Projekt Rentowny")
