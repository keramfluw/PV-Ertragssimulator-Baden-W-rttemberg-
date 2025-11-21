
# PV-Ertrags-Simulator Baden-Wuerttemberg (Version 3)

Diese Version enthaelt folgende Anpassungen:

- Dachneigung als Auswahl:
  - Flachdach (aufgestaendert 15 Grad)
  - Typisches Hausdach (30 Grad)
  - Pultdach mit Unterauswahl 20 / 30 / 40 Grad
- Ausrichtungsauswahl:
  - Sued mit einstellbarem Orientierungsgrad (60 bis 100 Prozent)
  - Ost/West mit pauschalem Faktor von 95 % gegenueber optimal Sued
- Nur ein "realistisches" Szenario (kein konservativ/optimistisch mehr).
- Alle Werte werden in einer Tabelle mit Tausenderpunkten und Prozentformat angezeigt.
- Balkendiagramm mit Zahlenlabels fuer Jahreserzeugung, Eigenverbrauch (mit Speicher)
  und Ueberschuss (mit Speicher).

Installation:

1. Python 3.10+ installieren.
2. Projekt entpacken und in das Verzeichnis wechseln.
3. Pakete installieren:

   pip install -r requirements.txt

4. App starten:

   streamlit run app.py
