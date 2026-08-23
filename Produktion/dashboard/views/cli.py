"""Darstellung auf der Kommandozeile.

Dient als Rueckfallebene, falls Streamlit nicht zur Verfuegung steht.
Die Ansicht enthaelt keine Fachlogik und stellt nur uebergebene Werte dar.
"""

from ..domaene import Leistungsstatus, Zielstatus, runde
from ..dto import DashboardDatenDTO

AMPEL = {
    Zielstatus.GRUEN: "[ gruen  ]",
    Zielstatus.GELB: "[ gelb   ]",
    Zielstatus.ROT: "[ rot    ]",
}
BREITE = 66


class CliView:
    def zeige(self, daten: DashboardDatenDTO) -> None:
        print("=" * BREITE)
        print(f"  STUDIEN-DASHBOARD  |  {daten.studiengang}")
        print(f"  Stand {daten.stichtag.strftime('%d.%m.%Y')}")
        print("=" * BREITE)
        self._fortschritt(daten)
        self._noten(daten)
        self._tempo(daten)
        self._module(daten)
        print("=" * BREITE)

    def _balken(self, anteil: float, breite: int = 40) -> str:
        voll = max(0, min(breite, round(anteil * breite)))
        return "#" * voll + "." * (breite - voll)

    def _fortschritt(self, daten: DashboardDatenDTO) -> None:
        f = daten.fortschritt
        anteil = f.erreichte_ects / f.gesamt_ects if f.gesamt_ects else 0.0
        print(f"\nZIEL 1  Studienfortschritt              {AMPEL[f.status]}")
        print(f"  [{self._balken(anteil)}] {anteil:5.1%}")
        print(f"  erreicht {f.erreichte_ects:6.1f} von {f.gesamt_ects} ECTS")
        for status in Leistungsstatus:
            wert = f.ects_nach_status.get(status, 0.0)
            if wert:
                print(f"    {status.value:<16} {wert:6.1f} ECTS")
        print(
            f"  Soll Zielbild    {f.soll_ects_zielbild:6.1f} ECTS  "
            f"({f.abweichung_ects:+.1f})"
        )
        print(
            f"  Soll Regelende   {f.soll_ects_regelende:6.1f} ECTS  "
            f"({f.vorsprung_regelende:+.1f})"
        )

    def _noten(self, daten: DashboardDatenDTO) -> None:
        n = daten.noten
        print(f"\nZIEL 2  Notendurchschnitt               {AMPEL[n.status]}")
        if n.durchschnitt is None:
            print("  noch keine bewertete Leistung vorhanden")
            return
        print(
            f"  aktuell {runde(n.durchschnitt):.2f}  "
            f"(aus {n.bewertete_ects:.0f} von {n.benotbare_ects:.0f} "
            f"benotbaren ECTS)"
        )
        if n.korridor:
            print(
                f"  erreichbarer Korridor {runde(n.korridor[0]):.2f} bis "
                f"{runde(n.korridor[1]):.2f}"
            )
        for ziel in n.ziele:
            rest = n.restschnitt_je_ziel.get(ziel.bezeichnung)
            text = "-" if rest is None else f"{runde(rest):.2f}"
            print(
                f"  {ziel.bezeichnung:<22} Ziel {ziel.zielwert:.1f}  "
                f"nötiger Restschnitt {text}  {AMPEL[ziel.status]}"
            )

    def _tempo(self, daten: DashboardDatenDTO) -> None:
        t = daten.tempo
        print(f"\nFRÜHINDIKATOR  Arbeitstempo            {AMPEL[t.status]}")
        print(f"  Ist                    {t.ist_tempo:5.2f} ECTS/Monat")
        print(f"  nötig bis Zielbild    {t.soll_tempo_zielbild:5.2f} ECTS/Monat")
        print(f"  nötig bis Regelende   {t.soll_tempo_regelende:5.2f} ECTS/Monat")

    def _module(self, daten: DashboardDatenDTO) -> None:
        if not daten.laufende_module:
            return
        print("\nLAUFENDE MODULE")
        for m in daten.laufende_module:
            note = "-" if m.note is None else f"{m.note:.1f}"
            print(
                f"  {m.bezeichnung[:44]:<44} {m.ects:>3} ECTS  "
                f"{m.status.value:<14} Note {note}"
            )
