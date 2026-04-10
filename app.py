import streamlit as st

# Ustawienia strony
st.set_page_config(page_title="Kalkulator BESS 10/40", layout="centered")

# Nagłówek i Stylistyka (podobnie jak na Twoim screenie)
st.title("🛠️ Konfiguracja Modelu Finansowego BESS 10/40")
st.markdown("---")

# --- SEKCJA SUWAKÓW (Inputy) ---
# Powielamy suwaki zgodnie z Twoimi wymaganiami
capex_eur = st.slider("CAPEX EUR", min_value=7000000, max_value=10000000, value=8700000, step=50000)
kurs = st.slider("Kurs EUR/PLN", min_value=4.00, max_value=4.70, value=4.30, step=0.01)
spread = st.slider("Spread SWAP [PLN/MWh]", min_value=200, max_value=600, value=380, step=10)
wibor = st.slider("WIBOR 3M [%]", min_value=4.00, max_value=8.00, value=5.85, step=0.05)
marza = st.slider("Marża Banku [%]", min_value=1.00, max_value=4.00, value=2.50, step=0.10)
lewar = st.slider("Lewar (LTV) [%]", min_value=50, max_value=85, value=70, step=5)

# --- LOGIKA OBLICZEŃ ---
# Parametry techniczne
MOC_MW = 10
POJ_MWH = 40
RYNEK_MOCY_MW = 6.130
CENA_RM = 244.90  # PLN/kW/rok (Aukcja 2029)
OPEX_ROCZNY = MOC_MW * 45000  # 45k PLN/MW

# Obliczenia finansowe
capex_pln = capex_eur * kurs
przychod_rm = RYNEK_MOCY_MW * 1000 * CENA_RM
przychod_swap = (POJ_MWH * 310 * 0.85) * spread  # 310 cykli, 85% sprawności
ebitda = (przychod_rm + przychod_swap) - OPEX_ROCZNY

# Obsługa długu
kwota_kredytu = capex_pln * (lewar / 100)
oprocentowanie = (wibor + marza) / 100
# Rata roczna (wzór na raty równe)
okres_lat = 10
if oprocentowanie > 0:
    rata = kwota_kredytu * (oprocentowanie / (1 - (1 + oprocentowanie)**-okres_lat))
else:
    rata = kwota_kredytu / okres_lat

dscr = ebitda / rata if rata > 0 else 0

# --- PREZENTACJA WYNIKÓW ---
st.markdown("---")
st.subheader("📊 Kluczowe Wyniki Finansowe")

col1, col2 = st.columns(2)
with col1:
    st.metric("Łączny CAPEX [PLN]", f"{capex_pln:,.0f} zł".replace(',', ' '))
    st.metric("Roczna EBITDA [PLN]", f"{ebitda:,.0f} zł".replace(',', ' '))

with col2:
    st.metric("Wskaźnik DSCR", f"{dscr:.2f}")
    st.metric("Roczna Rata Kredytu", f"{rata:,.0f} zł".replace(',', ' '))

# Status bankowalności
if dscr >= 1.25:
    st.success("✅ PROJEKT BANKOWALNY: DSCR powyżej progu bezpieczeństwa (1.25)")
elif dscr >= 1.10:
    st.warning("⚠️ WYMAGANA OPTYMALIZACJA: DSCR na granicy akceptowalności banku")
else:
    st.error("❌ RYZYKO FINANSOWE: DSCR poniżej wymogów bankowych")

st.markdown("---")
st.caption("Kalkulator przygotowany na potrzeby analizy BESS 10MW/40MWh z uwzględnieniem Rynku Mocy (2029) oraz kontraktu SWAP.")
