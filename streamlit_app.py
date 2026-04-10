import streamlit as st

st.set_page_config(page_title="BESS 10/40 Optimizer", layout="centered")

st.title("🔋 Optymalizator Projektu BESS 10MW/40MWh")
st.markdown("---")

# --- SEKCJA WEJŚCIOWA (Suwaki) ---
st.subheader("⚙️ Konfiguracja Finansowa")

capex_eur = st.slider("CAPEX Całkowity [EUR]", 7000000, 10000000, 8550000, step=50000)
kurs_eur = st.slider("Kurs EUR/PLN", 4.00, 4.70, 4.30, step=0.01)

st.markdown("---")
st.subheader("🏦 Parametry Bankowe")
lewar = st.slider("Lewar (LTV) [%]", 50, 85, 70, step=5)
wibor = st.slider("WIBOR 3M [%]", 4.00, 8.00, 5.85, step=0.05)
marza_banku = st.slider("Marża Banku [%]", 1.00, 4.00, 2.50, step=0.10)

st.markdown("---")
st.subheader("📈 Rynek i Operacje")
spread_swap = st.slider("Gwarantowany Spread SWAP [PLN/MWh]", 200, 600, 380, step=10)
opex_mw = st.slider("Koszt OPEX [PLN/MW/rok]", 30000, 70000, 45000, step=1000)

# --- LOGIKA OBLICZEŃ ---
# 1. CAPEX i Dług
capex_pln = capex_eur * kurs_eur
kwota_kredytu = capex_pln * (lewar / 100)
oprocentowanie_total = (wibor + marza_banku) / 100

# 2. Przychody (Rynek Mocy + SWAP)
# Dane z aukcji 2029: 6.130 MW * 244.90 PLN
przychod_rm = 6.130 * 1000 * 244.90
# Arbitraż: 40MWh * 310 dni * 85% sprawności * spread
przychod_swap = (40 * 310 * 0.85) * spread_swap
suma_przychodow = przychod_rm + przychod_swap

# 3. EBITDA i Obsługa długu
koszty_opex = 10 * opex_mw
ebitda = suma_przychodow - koszty_opex

# Rata roczna (10 lat spłaty)
n = 10 # lat
if oprocentowanie_total > 0:
    rata_roczna = kwota_kredytu * (oprocentowanie_total / (1 - (1 + oprocentowanie_total)**-n))
else:
    rata_roczna = kwota_kredytu / n

dscr = ebitda / rata_roczna if rata_roczna > 0 else 0

# --- WYNIKI ---
st.markdown("---")
st.header("📊 Wyniki Analizy")

c1, c2, c3 = st.columns(3)
c1.metric("EBITDA Roczna", f"{ebitda:,.0f} PLN")
c2.metric("Rata Kredytu", f"{rata_roczna:,.0f} PLN")
c3.metric("Wskaźnik DSCR", f"{dscr:.2f}")

# Alert bankowy
if dscr >= 1.25:
    st.success("✅ Projekt spełnia wymogi bankowe (DSCR > 1.25)")
else:
    st.error("❌ DSCR zbyt niski dla finansowania Project Finance")

st.info(f"Wkład własny inwestora (Equity): {capex_pln - kwota_kredytu:,.0f} PLN")
