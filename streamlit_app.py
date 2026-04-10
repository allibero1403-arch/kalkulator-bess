import streamlit as st
import pandas as pd

# Ustawienia szerokości strony dla lepszej czytelności
st.set_page_config(page_title="BESS 10MW/40MWh Optimizer", layout="wide")

st.title("🔋 Optymalizator Projektu Magazynu Energii 10MW / 40MWh")
st.markdown("Analiza finansowa uwzględniająca Rynek Mocy, SWAP oraz finansowanie dłużne (Leverage 70%)")
st.markdown("---")

# --- PASEK BOCZNY: NAKŁADY I FINANSOWANIE ---
with st.sidebar:
    st.header("🏗️ Inwestycja i Kursy")
    capex_eur = st.number_input("CAPEX Całkowity [EUR]", value=8550000, step=50000)
    kurs_eur = st.slider("Kurs EUR/PLN", 4.00, 4.70, 4.30, step=0.01)
    
    st.markdown("---")
    st.header("🏦 Finansowanie Bankowe")
    lewar = st.slider("Lewar (LTV) [%]", 50, 85, 70, step=5)
    wibor = st.slider("WIBOR 3M [%]", 4.00, 8.00, 5.85, step=0.05)
    marza_banku = st.slider("Marża Banku [%]", 1.00, 4.00, 2.50, step=0.10)
    okres_kredytu = st.number_input("Okres spłaty kredytu [Lata]", value=10)

# --- GŁÓWNY PANEL: PRZYCHODY I OPERACJE ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("⚡ Rynek Mocy (Gwarantowany 17 lat)")
    # Dane specyficzne użytkownika
    moc_rm = st.number_input("Obowiązek mocowy [MW]", value=6.130, step=0.001, format="%.3f")
    cena_rm = st.number_input("Cena z aukcji 2029 [PLN/kW/rok]", value=244.90, step=0.1)
    st.info(f"Roczny przychód stały: {moc_rm * 1000 * cena_rm:,.0f} PLN")

with col_right:
    st.subheader("🔄 SWAP i Arbitraż Rynkowy")
    spread_swap = st.slider("Gwarantowany Spread [PLN/MWh]", 200, 600, 380, step=10)
    opex_mw = st.slider("Koszty OPEX [PLN/MW/rok]", 30000, 70000, 45000, step=1000)
    st.caption("Założenia: 310 cykli rocznie, sprawność systemowa 85%")

# --- LOGIKA OBLICZEŃ FINANSOWYCH ---

# 1. CAPEX i Kapitały
capex_pln = capex_eur * kurs_eur
kwota_kredytu = capex_pln * (lewar / 100)
wklad_wlasny = capex_pln - kwota_kredytu
oprocentowanie_total = (wibor + marza_banku) / 100

# 2. Przychody Roczne (Revenue Stack)
# Przychód z Rynku Mocy: MW * 1000 (kW) * Cena
p_rynek_mocy = moc_rm * 1000 * cena_rm
# Przychód ze SWAP: Pojemność 40MWh * Cykle * Sprawność * Spread
p_swap = (40 * 310 * 0.85) * spread_swap
suma_przychodow = p_rynek_mocy + p_swap

# 3. EBITDA i Obsługa długu
koszty_opex_total = 10 * opex_mw
ebitda = suma_przychodow - koszty_opex_total

# Rata kredytu (Rata równa - annuitetowa)
if oprocentowanie_total > 0:
    rata_roczna = kwota_kredytu * (oprocentowanie_total / (1 - (1 + oprocentowanie_total)**-okres_kredytu))
else:
    rata_roczna = kwota_kredytu / okres_kredytu

dscr = ebitda / rata_roczna if rata_roczna > 0 else 0

# --- PREZENTACJA WYNIKÓW ---
st.markdown("---")
st.header("📊 Kluczowe Wskaźniki Projektu")

res1, res2, res3, res4 = st.columns(4)
res1.metric("Łączny CAPEX [PLN]", f"{capex_pln:,.0f}")
res2.metric("EBITDA Roczna [PLN]", f"{ebitda:,.0f}")
res3.metric("Roczna Rata [PLN]", f"{rata_roczna:,.0f}")
res4.metric("Wskaźnik DSCR", f"{dscr:.2f}")

# Wykres Struktury Przychodów
st.subheader("Struktura Przychodów: Rynek Mocy vs Arbitraż")
df_chart = pd.DataFrame({
    "Źródło przychodu": ["Rynek Mocy (Gwarancja)", "SWAP (Arbitraż)"],
    "Wartość [PLN]": [p_rynek_mocy, p_swap]
})
st.bar_chart(df_chart, x="Źródło przychodu", y="Wartość [PLN]", color="#1f77b4")

# Status Bankowalności
if dscr >= 1.25:
    st.success(f"✅ PROJEKT BANKOWALNY: Wskaźnik DSCR ({dscr:.2f}) powyżej wymaganego progu 1.25.")
else:
    st.error(f"❌ RYZYKO FINANSOWE: Wskaźnik DSCR ({dscr:.2f}) poniżej wymogów Project Finance (1.25).")

# Podsumowanie wkładu
st.write(f"**Kapitał własny (Equity) do zaangażowania:** {wklad_wlasny:,.0f} PLN")
st.markdown("---")
st.caption("Kalkulator BESS v3.0 | Projekt: 10MW/40MWh | Przyłącze SN | Rynek Mocy 2029-2046")
