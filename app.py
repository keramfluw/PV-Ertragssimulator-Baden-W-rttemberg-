
import streamlit as st
import pandas as pd
import math
import altair as alt

st.set_page_config(
    page_title="PV-Ertrags-Simulator Baden-Wuerttemberg",
    layout="wide"
)

# Global font styling (Times New Roman, etwas groesser fuer bessere Lesbarkeit)
# Zusaetzlich: Media Queries fuer bessere mobile Darstellung
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
    @media (max-width: 768px) {
        html, body, [class*="css"]  {
            font-size: 18px;
        }
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        table, th, td {
            font-size: 16px;
        }
    }
    </style>
    ''',
    unsafe_allow_html=True
)

st.title("PV-Ertrags-Simulator Baden-Wuerttemberg")

st.markdown(
    """
    Dieses Tool berechnet Jahresertraege, Eigenverbrauch, Ueberschuss und Speicherwirkung
    fuer PV-Anlagen in Konstanz und weiteren Staedten in Baden-Wuerttemberg.

    Die Berechnung ist bewusst vereinfachend und eignet sich fuer Grobabschaetzungen
    und erste Business-Case-Entwuerfe, nicht als Ersatz fuer detaillierte Ertragsgutachten. 
    by Wulfftechnologies 2025
    """
)

with st.expander("Hinweise fuer mobile Nutzung (Smartphone / Tablet)"):
    st.markdown(
        """
        - Am besten im Hochformat starten, bei Bedarf ins Querformat wechseln.
        - Die Seitenleiste (Eingaben) kann ueber den kleinen Pfeil am linken Rand
          ein- und ausgeblendet werden, um mehr Platz fuer Tabelle und Diagramm zu haben.
        - Tabellen und Diagramme sind fuer kleinere Bildschirme zusaetzlich vergroessert.
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

# Standort
selected_city = st.sidebar.selectbox(
    "Stadt in Baden-Wuerttemberg",
    options=sorted(CITY_DATA.keys()),
    index=sorted(CITY_DATA.keys()).index("Konstanz") if "Konstanz" in CITY_DATA else 0,
)

# Anlagengroesse
plant_size_kwp = st.sidebar.slider(
    "Anlagengroesse (kWp)",
    min_value=10.0,
    max_value=50000.0,
    value=1000.0,
    step=10.0,
    help="Spanne von 10 kWp bis 50.000 kWp (50 MWp)."
)

# Dachtyp und Neigung
st.sidebar.subheader("Dachtyp und Neigung")

roof_type = st.sidebar.selectbox(
    "Dachtyp",
    options=[
        "Flachdach (aufgestaendert 15 Grad)",
        "Typisches Hausdach (30 Grad)",
        "Pultdach (20/30/40 Grad)"
    ]
)

if roof_type == "Flachdach (aufgestaendert 15 Grad)":
    roof_tilt_deg = 15
elif roof_type == "Typisches Hausdach (30 Grad)":
    roof_tilt_deg = 30
else:
    pult_angle = st.sidebar.radio(
        "Neigung Pultdach (Grad)",
        options=[20, 30, 40],
        index=1
    )
    roof_tilt_deg = pult_angle

# Ausrichtung
st.sidebar.subheader("Ausrichtung")

orientation_mode = st.sidebar.selectbox(
    "Ausrichtung",
    options=[
        "Sued (mit prozentualem Orientierungsgrad)",
        "Ost/West"
    ]
)

if orientation_mode.startswith("Sued"):
    south_quality = st.sidebar.slider(
        "Orientierungsgrad gegenueber optimaler Sued-Ausrichtung (%)",
        min_value=60,
        max_value=100,
        value=90,
        step=10,
        help="Bewertung der tatsaechlichen Ausrichtung im Vergleich zu ideal Sued."
    )
    orientation_factor = south_quality / 100.0
    orientation_description = f"Sued, {south_quality} % von optimal"
else:
    # Pauschaler Faktor fuer Ost/West-Ausrichtung (vereinfachte Annahme)
    orientation_factor = 0.95
    orientation_description = "Ost/West (pauschal 95 % von optimal Sued)"

# Eigenverbrauch und Speicher
st.sidebar.subheader("Eigenverbrauch und Speicher")

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

def tilt_correction_factor(tilt_deg: float) -> float:
    ideal = 30.0
    diff = abs(tilt_deg - ideal)
    loss_per_10deg = 0.02
    factor = 1.0 - loss_per_10deg * (diff / 10.0)
    return max(0.85, min(1.05, factor))

def compute_results(
    city: str,
    base_specific_yield: float,
    tilt_deg: float,
    orientation_factor: float,
    plant_kwp: float,
    self_consumption_share_pct: float,
    battery_kwh: float,
    battery_cycles: int,
):
    tilt_factor = tilt_correction_factor(tilt_deg)
    specific_yield = base_specific_yield * tilt_factor * orientation_factor

    annual_generation = plant_kwp * specific_yield

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
        "Spezifischer Ertrag (kWh/kWp*a)": round(specific_yield, 1),
        "Anlagengroesse (kWp)": plant_kwp,
        "Jahreserzeugung (kWh/a)": round(annual_generation, 0),
        "Eigenverbrauch ohne Speicher (kWh/a)": round(direct_self_consumption, 0),
        "Ueberschuss ohne Speicher (kWh/a)": round(surplus_before_storage, 0),
        "Zusaetzliche Nutzung durch Speicher (kWh/a)": round(shifted_energy, 0),
        "Eigenverbrauch mit Speicher (kWh/a)": round(self_consumption_with_storage, 0),
        "Ueberschuss mit Speicher (kWh/a)": round(surplus_after_storage, 0),
        "Autarkie ohne Speicher (Prozent)": round(autarky_without_storage, 1),
        "Autarkie mit Speicher (Prozent)": round(autarky_with_storage, 1),
        "Dachneigung (Grad)": tilt_deg,
        "Ausrichtung": orientation_description
    }

base_specific_yield_city = CITY_DATA[selected_city]

result = compute_results(
    city=selected_city,
    base_specific_yield=base_specific_yield_city,
    tilt_deg=roof_tilt_deg,
    orientation_factor=orientation_factor,
    plant_kwp=plant_size_kwp,
    self_consumption_share_pct=base_self_consumption_share,
    battery_kwh=battery_size_kwh,
    battery_cycles=battery_cycles_per_year,
)

st.subheader("Eingesetzte standortbezogene Referenzdaten")
with st.expander("Liste der hinterlegten Staedte und spezifischen Ertraege (ohne Korrekturen)"):
    st.dataframe(cities_df, use_container_width=True)

st.subheader("Ergebnis (realistische Annahme)")

results_df = pd.DataFrame([result])

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

st.subheader("Visualisierung: Erzeugung, Eigenverbrauch und Ueberschuss (mit Speicher)")

chart_df = pd.DataFrame(
    {
        "Kategorie": [
            "Jahreserzeugung gesamt",
            "Eigenverbrauch mit Speicher",
            "Ueberschuss mit Speicher"
        ],
        "Wert": [
            result["Jahreserzeugung (kWh/a)"],
            result["Eigenverbrauch mit Speicher (kWh/a)"],
            result["Ueberschuss mit Speicher (kWh/a)"]
        ]
    }
)

bar = alt.Chart(chart_df).mark_bar().encode(
    x=alt.X("Kategorie:N", sort=None),
    y=alt.Y("Wert:Q")
).properties(
    width="container",
    height=400
)

text = bar.mark_text(
    align="center",
    baseline="bottom",
    dy=-5
).encode(
    text=alt.Text("Wert:Q", format=",.0f")
)

st.altair_chart(bar + text, use_container_width=True)

st.markdown(
    "Hinweis: Die Speicherwirkung wird stark vereinfacht modelliert. "
    "Fuer praezise Auslegungen (Lastgaenge, 15-Minuten-Profile, Temperatur, Degradation) "
    "sind spezialisierte Simulationswerkzeuge erforderlich."
)
