import streamlit as st
import pandas as pd

# Ustawienie szerokości strony
st.set_page_config(page_title="BESS 10MW/40MWh Optimizer", layout="centered")

# --- TYTUŁ ---
st.title("🔋 Kalkulator Inwestycyjny BESS 10MW / 40MWh")
st.markdown("Analiza rentowności: Rynek Mocy (2029) + SWAP Arbitrażowy")
st.markdown("---")

# --- SEKCJA 1: NAKŁADY I FINANSOWANIE ---
st.header("🏗️ 1. Nakłady Inwestycyjne i Bank")
col_capex1, col_capex2 = st.columns(2)

with col_capex1:
    capex_eur = st.number_input("CAPEX Całkowity [EUR]", value=8550000, step=50000)
    kurs_eur = st.slider("Kurs EUR/PLN", 4.00, 4.70, 4.30, step=0.01)

with col_capex2:
    lewar = st.slider("Lewar (LTV) [%]", 50, 85, 70, step=5)
    wibor = st.slider("WIBOR 3M [%]", 4.00, 8.00, 5.85, step=0.05)
    marza_banku = st.slider("Marża Banku [%]", 1.00, 4.00, 2.50, step=0.10)

st.markdown("---")

# --- SEKCJA 2: PRZYCHODY (KLUCZOWE ZAŁOŻENIA) ---
st.header("📈 2. Założenia Przychodowe")

# RYNEK MOCY - WYRÓŻNIONY
st.subheader("⚡ Rynek Mocy (Fundament Gwarantowany)")
rm_col1, rm_col2 = st.columns(2)
with rm_col1:
    moc_rm = st.number_input("Obowiązek mocowy [MW]", value=6.130, step=0.001, format="%.3f")
with rm_col2:
    cena_rm = st.number_input("Cena aukcji 2029 [PLN/kW/rok]", value=244.90, step=0.1)

# ARBITRAŻ / SWAP
st.subheader("🔄 Arbitraż Energetyczny (Zabezpieczony SWAP)")
swap_col1, swap_col2 = st.columns(2)
with swap_col1:
    spread_swap = st.slider("Gwarantowany Spread [PLN/MWh]", 200, 600, 380, step=10)
with swap_col2:
    opex_mw = st.slider("Koszty OPEX [PLN/MW/rok]", 30000, 70000, 45000, step=1000)

st.markdown("---")

# --- LOGIKA OBLICZEŃ ---
# Finanse
capex_pln = capex_eur * kurs_eur
kwota_kredytu = capex_pln * (lewar / 100)
oprocentowanie = (wibor + marza_banku) / 100

# Revenue Stack
p_rynek_mocy = moc_rm * 1000 * cena_rm
p_swap = (40 * 310 * 0.85) * spread_swap
suma_przychodow = p_rynek_mocy + p_swap

# EBITDA i Rata
ebitda = suma_przychodow - (10 * opex_mw)
n_lat = 10
if oprocentowanie > 0:
    rata_roczna = kwota_kredytu * (oprocentowanie / (1 - (1 + oprocentowanie)**-n_lat))
else:
    rata_roczna = kwota_kredytu / n_lat

dscr = ebitda / rata_roczna if rata_roczna > 0 else 0

# --- SEKCJA 3: WYNIKI FINANSOWE ---
st.header("📊 3. Wyniki Finansowe i Bankowalność")

# Liczniki (Metrics)
m1, m2, m3 = st.columns(3)
m1.metric("EBITDA Roczna", f"{ebitda:,.0f} PLN")
m2.metric("Roczna Rata Kredytu", f"{rata_roczna:,.0f} PLN")
m3.metric("Wskaźnik DSCR", f"{dscr:.2f}")

# --- POPRAWIONY WYKRES ---
st.subheader("Struktura Przychodów Rocznych")

# Tworzymy czystą tabelę danych
chart_data = pd.DataFrame({
    "Zrodlo": ["Rynek Mocy", "Arbitraz (SWAP)"],
    "Wartość": [float(p_rynek_mocy), float(p_swap)] # Wymuszamy format liczbowy
})

# Wyświetlamy wykres z wyraźnym przypisaniem osi
st.bar_chart(
    data=chart_data, 
    x="Zrodlo", 
    y="Wartość", 
    color="#004aad",
    use_container_width=True
)

# Dodatkowa tabela pod wykresem dla pewności (możesz usunąć jeśli nie chcesz)
st.table(chart_data.set_index("Zrodlo"))
