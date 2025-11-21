
# PV-Ertrags-Simulator Baden-Wuerttemberg (Version mit besserer Darstellung)

Dieses Projekt enthaelt eine Streamlit-App, mit der Sie fuer
PV-Anlagen zwischen 10 kWp und 50 MWp in Konstanz und weiteren
Staedten in Baden-Wuerttemberg Jahresertraege, Eigenverbrauch,
Ueberschuss sowie Speicherwirkung in drei Szenarien abschaetzen koennen.

Diese Version bietet:
- Allgemeine Schrift in Times New Roman mit groesserer Schriftgroesse,
- Tabelle mit Tausendertrennung per Punkt fuer kWp- und kWh-Werte,
- Prozente mit einer Nachkommastelle,
- Balkendiagramm mit direkten Zahlenlabels auf den Balken.

Installationsschritte:

1. Python 3.10+ installieren.
2. Projekt entpacken und in das Verzeichnis wechseln.
3. Pakete installieren:

   pip install -r requirements.txt

4. App starten:

   streamlit run app.py
