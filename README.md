
# PV-Ertrags-Simulator Baden-Wuerttemberg (Version 4, mobil optimiert)

Diese Version basiert auf Version 3 und ergaenzt eine Optimierung fuer die
Nutzung auf Mobiltelefonen:

- Groessere Standardschrift fuer bessere Lesbarkeit.
- Zusaetzliche Media-Queries fuer kleine Bildschirmbreiten (z. B. Smartphones):
  - Erhoehte Schriftgroesse,
  - reduzierte Seitenraender,
  - besser lesbare Tabellen.
- Ein eigener Abschnitt "Hinweise fuer mobile Nutzung" mit Tipps zum Umgang mit der
  Seitenleiste auf kleinen Screens.

Alle fachlichen Funktionen aus Version 3 bleiben erhalten:

- Dachneigung als Auswahl (Flachdach 15 Grad, Hausdach 30 Grad, Pultdach 20/30/40 Grad).
- Ausrichtungsauswahl (Sued mit prozentualem Orientierungsgrad oder Ost/West mit pauschalem Faktor).
- Nur ein "realistisches" Szenario.
- Tabelle mit Tausenderpunkten und Prozentformat.
- Balkendiagramm mit Zahlenlabels fuer Jahreserzeugung, Eigenverbrauch (mit Speicher)
  und Ueberschuss (mit Speicher).

Installation:

1. Python 3.10+ installieren.
2. Projekt entpacken und in das Verzeichnis wechseln.
3. Pakete installieren:

   pip install -r requirements.txt

4. App starten:

   streamlit run app.py
