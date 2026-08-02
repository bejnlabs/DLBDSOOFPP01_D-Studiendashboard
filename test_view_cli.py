"""
Machbarkeitstest 3 - Bedienoberflaeche ueber die Kommandozeile.

Frage aus der Aufgabenstellung (Konzeptionsphase, Punkt 4):
"Soll die Interaktion mit dem Benutzer ueber die Kommandozeile oder
ueber eine grafische Bedienoberflaeche erfolgen?"

Ziel dieses Tests:
Nachweisen, dass die Dashboard-Kennzahlen auch ohne grafische
Oberflaeche vollstaendig darstellbar sind. Diese Variante dient
spaeter als Rueckfallebene, falls die Streamlit-Installation
beim Pruefenden nicht gelingt.

Verwendete Bibliotheken: keine (nur Standardbibliothek).
Start: python test_view_cli.py
Kompatibel ab Python 3.10.
"""

from dashboard_daten import beispieldaten, kennzahlen, GESAMT_ECTS


def balken(anteil: float, breite: int = 30) -> str:
    """Erzeugt einen einfachen Textbalken."""
    gefuellt = round(anteil * breite)
    return "#" * gefuellt + "." * (breite - gefuellt)


def main() -> None:
    daten = kennzahlen(beispieldaten())

    print("=" * 58)
    print("  STUDIEN-DASHBOARD (Kommandozeilen-Variante)")
    print("=" * 58)

    print("\nZiel 1 - Studienfortschritt")
    print(f"  [{balken(daten['fortschritt'])}] {daten['fortschritt']:.1%}")
    print(f"  abgeschlossen {daten['abgeschlossen']:>3.0f} ECTS")
    print(f"  laufend       {daten['laufend']:>3.0f} ECTS")
    print(f"  offen         {daten['offen']:>3.0f} ECTS")
    print(f"  gesamt        {GESAMT_ECTS:>3} ECTS")

    print("\nZiel 2 - Notendurchschnitt")
    if daten["schnitt"] is None:
        print("  noch keine bewertete Leistung vorhanden")
    else:
        print(f"  aktuell {daten['schnitt']:.2f} "
              f"(aus {daten['ects_bewertet']:.0f} von "
              f"{daten['ects_benotbar_gesamt']:.0f} benotbaren ECTS)")
        print(f"  noetiger Restschnitt fuer 2,0: "
              f"{daten['restschnitt_wunsch']:.2f}")
        print(f"  noetiger Restschnitt fuer 2,5: "
              f"{daten['restschnitt_realistisch']:.2f}")

    print("\n" + "=" * 58)


if __name__ == "__main__":
    main()
