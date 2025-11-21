
import streamlit as st
import pandas as pd
import math
import altair as alt

st.set_page_config(
    page_title="PV-Ertrags-Simulator Baden-Wuerttemberg",
    layout="wide"
)

# Global font styling (Times New Roman, etwas groesser fuer bessere Lesbarkeit)
st.markdown(
    '''
    <style>
    html, body, [class*="css"]  {
        font-family: "Times New Roman", serif;
        font-size: 15px;
    }
    table, th, td {
        font-family: "Times New Roman", serif;
        font-size: 15px;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

st.title("PV-Ertrags-Simulator Baden-Wuerttemberg (10 kWp bis 50 MWp)")

st.markdown(
    """
    Dieses Tool berechnet Jahresertraege, Eigenverbrauch, Ueberschuss und Speicherwirkung
    fuer PV-Anlagen in Konstanz und weiteren Staedten in Baden-Wuerttemberg.
    
    Die Berechnung ist bewusst vereinfachend und eignet sich fuer Grobabschaetzungen,
    Szenarien und erste Business-Case-Entwuerfe, nicht als Ersatz fuer detaillierte
    Ertragsgutachten. copyright Wulfftechnologies e.K. 2025
    """
)

CITY_DATA = {
    "Konstanz": 1000,
    "Freiburg im Breisgau": 1050,
    "Stuttgart": 1000,
    "Karlsruhe": 1020,
    "Mannheim": 1020,
    "Heidelberg": 1020,
    "Ulm": 980,
    "Tuebingen": 980,
    "Heilbronn": 1000,
    "Pforzheim": 1000,
    "Reutlingen": 980,
    "Ravensburg": 990,
    "Villingen-Schwenningen": 960,
    "Offenburg": 1020,
    "Loerrach": 1050,
    "Baden-Baden": 1020
}

cities_df = pd.DataFrame(
    [{"Stadt": c, "Spezifischer Ertrag (kWh/kWp*a)": v} for c, v in CITY_DATA.items()]
).sort_values("Stadt")

st.sidebar.header("Eingabeparameter")

selected_city = st.sidebar.selectbox(
    "Stadt in Baden-Wuerttemberg",
    options=sorted(CITY_DATA.keys()),
    index=sorted(CITY_DATA.keys()).index("Konstanz") if "Konstanz" in CITY_DATA else 0,
)

plant_size_kwp = st.sidebar.slider(
    "Anlagengroesse (kWp)",
    min_value=10.0,
    max_value=50000.0,
    value=1000.0,
    step=10.0,
    help="Spanne von 10 kWp bis 50.000 kWp (50 MWp)."
)

roof_tilt_deg = st.sidebar.slider(
    "Dachneigung (Grad)",
    min_value=0,
    max_value=60,
    value=20,
    step=1,
    help="Vereinfachte Korrektur des spezifischen Ertrags je nach Dachneigung."
)

base_self_consumption_share = st.sidebar.slider(
    "Eigenverbrauchsanteil ohne Speicher (Prozent)",
    min_value=0,
    max_value=100,
    value=40,
    step=5,
    help="Direkter Eigenverbrauchsanteil ohne Speicher, bezogen auf die Jahreserzeugung."
)

battery_size_kwh = st.sidebar.number_input(
    "Speichergroesse (kWh nutzbar)",
    min_value=0.0,
    value=0.0,
    step=10.0,
    help="Nutzbare Speicherkapazitaet. 0 = kein Speicher."
)

battery_cycles_per_year = st.sidebar.slider(
    "Durchschnittliche Vollzyklen pro Jahr",
    min_value=50,
    max_value=365,
    value=250,
    step=5,
    help="Grobe Annahme, wie oft der Speicher pro Jahr vollstaendig geladen/entladen wird."
)

st.sidebar.markdown("---")
st.sidebar.subheader("Szenarien-Faktoren")
st.sidebar.markdown(
    "Die spezifischen Ertraege werden pro Szenario mit Faktoren skaliert."
)

factor_conservative = st.sidebar.slider(
    "Faktor konservativ",
    min_value=0.7,
    max_value=1.0,
    value=0.9,
    step=0.01,
)

factor_realistic = st.sidebar.slider(
    "Faktor realistisch",
    min_value=0.9,
    max_value=1.1,
    value=1.0,
    step=0.01,
)

factor_optimistic = st.sidebar.slider(
    "Faktor optimistisch",
    min_value=1.0,
    max_value=1.3,
    value=1.1,
    step=0.01,
)

def tilt_correction_factor(tilt_deg: float) -> float:
    ideal = 30.0
    diff = abs(tilt_deg - ideal)
    loss_per_10deg = 0.02
    factor = 1.0 - loss_per_10deg * (diff / 10.0)
    return max(0.85, min(1.05, factor))

def compute_scenario_results(
    city: str,
    base_specific_yield: float,
    tilt_deg: float,
    scenario_factor: float,
    plant_kwp: float,
    self_consumption_share_pct: float,
    battery_kwh: float,
    battery_cycles: int,
):
    tilt_factor = tilt_correction_factor(tilt_deg)
    specific_yield_scenario = base_specific_yield * tilt_factor * scenario_factor

    annual_generation = plant_kwp * specific_yield_scenario

    direct_self_consumption = annual_generation * (self_consumption_share_pct / 100.0)

    surplus_before_storage = max(0.0, annual_generation - direct_self_consumption)

    if battery_kwh > 0 and battery_cycles > 0:
        max_shifted_energy = battery_kwh * battery_cycles
    else:
        max_shifted_energy = 0.0

    shifted_energy = min(surplus_before_storage, max_shifted_energy)

    self_consumption_with_storage = direct_self_consumption + shifted_energy
    surplus_after_storage = max(0.0, annual_generation - self_consumption_with_storage)

    autarky_without_storage = (
        direct_self_consumption / annual_generation * 100.0
        if annual_generation > 0
        else 0.0
    )
    autarky_with_storage = (
        self_consumption_with_storage / annual_generation * 100.0
        if annual_generation > 0
        else 0.0
    )

    return {
        "Stadt": city,
        "Spezifischer Ertrag (kWh/kWp*a)": round(specific_yield_scenario, 1),
        "Anlagengroesse (kWp)": plant_kwp,
        "Jahreserzeugung (kWh/a)": round(annual_generation, 0),
        "Eigenverbrauch ohne Speicher (kWh/a)": round(direct_self_consumption, 0),
        "Ueberschuss ohne Speicher (kWh/a)": round(surplus_before_storage, 0),
        "Zusaetzliche Nutzung durch Speicher (kWh/a)": round(shifted_energy, 0),
        "Eigenverbrauch mit Speicher (kWh/a)": round(self_consumption_with_storage, 0),
        "Ueberschuss mit Speicher (kWh/a)": round(surplus_after_storage, 0),
        "Autarkie ohne Speicher (Prozent)": round(autarky_without_storage, 1),
        "Autarkie mit Speicher (Prozent)": round(autarky_with_storage, 1),
    }

base_specific_yield_city = CITY_DATA[selected_city]

results = {}
results["Konservativ"] = compute_scenario_results(
    city=selected_city,
    base_specific_yield=base_specific_yield_city,
    tilt_deg=roof_tilt_deg,
    scenario_factor=factor_conservative,
    plant_kwp=plant_size_kwp,
    self_consumption_share_pct=base_self_consumption_share,
    battery_kwh=battery_size_kwh,
    battery_cycles=battery_cycles_per_year,
)

results["Realistisch"] = compute_scenario_results(
    city=selected_city,
    base_specific_yield=base_specific_yield_city,
    tilt_deg=roof_tilt_deg,
    scenario_factor=factor_realistic,
    plant_kwp=plant_size_kwp,
    self_consumption_share_pct=base_self_consumption_share,
    battery_kwh=battery_size_kwh,
    battery_cycles=battery_cycles_per_year,
)

results["Optimistisch"] = compute_scenario_results(
    city=selected_city,
    base_specific_yield=base_specific_yield_city,
    tilt_deg=roof_tilt_deg,
    scenario_factor=factor_optimistic,
    plant_kwp=plant_size_kwp,
    self_consumption_share_pct=base_self_consumption_share,
    battery_kwh=battery_size_kwh,
    battery_cycles=battery_cycles_per_year,
)

st.subheader("Eingesetzte standortbezogene Referenzdaten")
with st.expander("Liste der hinterlegten Staedte und spezifischen Ertraege (ohne Korrekturen)"):
    st.dataframe(cities_df, use_container_width=True)

st.subheader("Szenario-Ergebnisse im Vergleich")

results_table = []
for scenario_name, data in results.items():
    row = {"Szenario": scenario_name}
    row.update(data)
    results_table.append(row)

results_df = pd.DataFrame(results_table)

# Kopie fuer Darstellung mit Tausenderpunkten
display_df = results_df.copy()

thousand_cols = [
    "Anlagengroesse (kWp)",
    "Jahreserzeugung (kWh/a)",
    "Eigenverbrauch ohne Speicher (kWh/a)",
    "Ueberschuss ohne Speicher (kWh/a)",
    "Zusaetzliche Nutzung durch Speicher (kWh/a)",
    "Eigenverbrauch mit Speicher (kWh/a)",
    "Ueberschuss mit Speicher (kWh/a)",
]

for col in thousand_cols:
    display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}".replace(",", "."))

percent_cols = [
    "Autarkie ohne Speicher (Prozent)",
    "Autarkie mit Speicher (Prozent)",
]

for col in percent_cols:
    display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}".replace(".", ","))

st.dataframe(display_df, use_container_width=True)

st.subheader("Visualisierung: Erzeugung, Eigenverbrauch und Ueberschuss")

metric_option = st.selectbox(
    "Zu visualisierende Kennzahl",
    options=[
        "Jahreserzeugung (kWh/a)",
        "Eigenverbrauch mit Speicher (kWh/a)",
        "Ueberschuss mit Speicher (kWh/a)",
        "Autarkie mit Speicher (Prozent)",
    ],
)

chart_df = results_df[["Szenario", metric_option]].rename(columns={metric_option: "Wert"})

# Balkendiagramm mit Zahlenlabels
bar = alt.Chart(chart_df).mark_bar().encode(
    x=alt.X("Szenario:N", sort=["Konservativ", "Realistisch", "Optimistisch"]),
    y=alt.Y("Wert:Q")
)

text = bar.mark_text(
    align="center",
    baseline="bottom",
    dy=-5  # etwas oberhalb der Balken
).encode(
    text=alt.Text("Wert:Q", format=",.0f")
)

st.altair_chart(bar + text, use_container_width=True)

st.markdown(
    "Hinweis: Die Speicherwirkung wird stark vereinfacht modelliert. "
    "Fuer praezise Auslegungen (Lastgaenge, 15-Minuten-Profile, Temperatur, Degradation) "
    "sind spezialisierte Simulationswerkzeuge erforderlich."
)
