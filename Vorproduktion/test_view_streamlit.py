"""
Machbarkeitstest 4 - Grafische Bedienoberflaeche mit Streamlit.

Frage aus der Aufgabenstellung (Konzeptionsphase, Punkt 4):
"Welche Python Bibliotheken sollen warum zum Einsatz kommen?" und
"Kommandozeile oder grafische Bedienoberflaeche?"

Ziel dieses Tests:
Nachweisen, dass sich dieselben Kennzahlen wie in der
Kommandozeilen-Variante mit geringem Aufwand grafisch darstellen
lassen - insbesondere Fortschrittsbalken und Kennzahlenkacheln.

Entscheidend: Diese Datei enthaelt KEINE Berechnung. Die gesamte
Fachlogik liegt in dashboard_daten.py und wird nur aufgerufen.
Damit ist bereits hier die Trennung von Darstellung und Logik
umgesetzt, die das Schichtenmodell aus Phase 2 verlangt.

Start (Windows, ohne venv-Aktivierung):
    .venv\\Scripts\\python.exe -m streamlit run test_view_streamlit.py
Getestet mit Streamlit 1.58.0 auf Python 3.14.5.
"""

import streamlit as st

from dashboard_daten import (beispieldaten, kennzahlen, GESAMT_ECTS,
                             ZIELNOTE_WUNSCH, ZIELNOTE_REALISTISCH)

st.set_page_config(page_title="Studien-Dashboard", layout="centered")

daten = kennzahlen(beispieldaten())

st.title("Studien-Dashboard")
st.caption("Machbarkeitstest Phase 1 - Platzhalterdaten")

st.subheader("Ziel 1: Studienfortschritt")
st.progress(daten["fortschritt"])
st.write(f"{daten['abgeschlossen']:.0f} von {GESAMT_ECTS} ECTS "
         f"({daten['fortschritt']:.1%})")

spalte1, spalte2, spalte3 = st.columns(3)
spalte1.metric("Abgeschlossen", f"{daten['abgeschlossen']:.0f} ECTS")
spalte2.metric("Laufend", f"{daten['laufend']:.0f} ECTS")
spalte3.metric("Offen", f"{daten['offen']:.0f} ECTS")

st.divider()

st.subheader("Ziel 2: Notendurchschnitt")
if daten["schnitt"] is None:
    st.info("Noch keine bewertete Leistung vorhanden.")
else:
    links, rechts = st.columns(2)
    links.metric("Aktueller Schnitt", f"{daten['schnitt']:.2f}")
    rechts.metric("Bewertete ECTS",
                  f"{daten['ects_bewertet']:.0f} / "
                  f"{daten['ects_benotbar_gesamt']:.0f}")

    st.write(f"Noetiger Restschnitt fuer Ziel {ZIELNOTE_WUNSCH:.1f}: "
             f"**{daten['restschnitt_wunsch']:.2f}**")
    st.write(f"Noetiger Restschnitt fuer Ziel {ZIELNOTE_REALISTISCH:.1f}: "
             f"**{daten['restschnitt_realistisch']:.2f}**")
