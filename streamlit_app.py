import streamlit as st
import pandas as pd

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="BESS 10/40 Optimizer", layout="wide")

st.title("🔋 Optymalizator Projektu BESS 10MW/40MWh")
st.markdown("Analiza rentowności z uwzględnieniem Rynku Mocy i kontraktu SWAP")
st.markdown("---")

# --- PASEK BOCZNY: PARAMETRY TECHNICZNE I BANKOWE ---
with st.sidebar:
    st.header("🏗️ Nakłady i Finansowanie")
    capex_eur = st.number_input("CAPEX Całkowity [EUR]", value=8550000, step=50000)
    kurs_eur = st.slider("Kurs EUR/PLN", 4.00, 4.70, 4.30, step=0.01)
    
    st.markdown("---")
    st.header("🏦 Parametry Kredytu")
    lewar = st.slider("Lewar (LTV) [%]", 50, 85, 70, step=5)
    wibor = st.slider("WIBOR 3M [%]", 4.00, 8.00, 5.85, step=0.05)
    marza_banku = st.slider("Marża Banku [%]", 1.00, 4.00, 2.50, step=0.10)
    okres_kredytu = st.number_input("Okres spłaty [Lata]", value=10)

# --- GŁÓWNY PANEL: PRZYCHODY I OPERACJE ---
col_in1, col_in2 = st.columns(2)

with col_in1:
    st.subheader("⚡ Rynek Mocy (Aukcja 2029)")
    # Dane Twojego projektu
    moc_rm = st.number_input("Obowiązek mocowy [MW]", value=6.130, step=0.001, format="%.3f")
    cena_rm = st.number_input("Cena z aukcji [PLN/kW/rok]", value=244.90, step=0.1)
    st.caption("Kontrakt gwarantowany na 17 lat")

with col_in2:
    st.subheader("🔄 Arbitraż i SWAP")
    spread_swap = st.slider("Gwarantowany Spread [PLN/MWh]", 200, 600, 380, step=10)
    opex_mw = st.slider("Koszt OPEX [PLN/MW/rok]", 30000, 70000, 45000, step=1000)
    st.caption("Założenie: 310 cykli rocznie, sprawność 85%")

# --- LOGIKA OBLICZEŃ ---
# 1. Finanse podstawowe
capex_pln = capex_eur * kurs_eur
kwota_kredytu = capex_pln * (lewar / 100)
wklad_wlasny = capex_pln - kwota_kredytu
oprocentowanie = (wibor + marza_banku) / 100

# 2. Przychody roczne
# Rynek Mocy: MW * 1000 (przeliczenie na kW) * Cena
p_rynek_mocy = moc_rm * 1000 * cena_rm
# SWAP: Pojemność * Cykle * Sprawność * Spread
p_swap = (40 * 310 * 0.85) * spread_swap
suma_przychodow = p_rynek_mocy + p_swap

# 3. EBITDA i Obsługa długu
koszty_opex = 10 * opex_mw
ebitda = suma_przychodow - koszty_opex

# Rata kredytu (formuła PMT)
if oprocentowanie > 0:
    rata_roczna = kwota_kredytu * (oprocentowanie / (1 - (1 + oprocentowanie)**-okres_kredytu))
else:
    rata_roczna = kwota_kredytu / okres_kredytu

dscr = ebitda / rata_roczna if rata_roczna > 0 else 0

# --- PREZENTACJA WYNIKÓW ---
st.markdown("---")
st.header("📊 Wyniki i Wskaźniki Bankowe")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Łączny CAPEX", f"{capex_pln:,.0f} PLN")
m2.metric("EBITDA Roczna", f"{ebitda:,.0f} PLN")
m3.metric("Roczna Rata", f"{rata_roczna:,.0f} PLN")
m4.metric("Wskaźnik DSCR", f"{dscr:.2f}")

# Wykres Struktury Przychodów
st.subheader("Struktura Przychodów: Rynek Mocy vs Arbitraż")
df_chart = pd.DataFrame({
    "Źródło": ["Rynek Mocy (Stały)", "SWAP (Zmienny/Zabezpieczony)"],
    "PLN": [p_rynek_mocy, p_swap]
})
st.bar_chart(df_chart, x="Źródło", y="PLN", color="#1f77b4")

# Podsumowanie i status bankowalności
if dscr >= 1.25:
    st.success(f"✅ PROJEKT BANKOWALNY. Wskaźnik DSCR ({dscr:.2f}) powyżej wymaganego progu 1.25.")
else:
    st.error(f"❌ RYZYKO FINANSOWE. Wskaźnik DSCR ({dscr:.2f}) poniżej progu 1.25. Wymagana optymalizacja kosztów lub wyższy spread.")

st.info(f"**Kapitał własny do zaangażowania (Equity):** {wklad_wlasny:,.0f} PLN")

st.markdown("---")
st.caption("Kalkulator BESS v2.0 | Dane oparte na aukcji Rynku Mocy 2029 oraz rynkowych kosztach technologii Li-ion.")
