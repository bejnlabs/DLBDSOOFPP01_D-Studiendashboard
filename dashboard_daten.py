"""
Gemeinsame Datenquelle fuer die Machbarkeitstests 3 und 4.

Zweck: Beide Bedienoberflaechen (Kommandozeile und Streamlit) greifen auf
dieselbe Funktion zu. Damit wird geprueft, ob sich Darstellung und
Berechnung sauber trennen lassen - eine Vorbedingung fuer das
Schichtenmodell aus Phase 2.

ACHTUNG: Die Noten und Module sind Platzhalter und muessen durch die echten
Werte ersetzt werden. Die Struktur ist entscheidend, nicht die Zahlen.

Kompatibel ab Python 3.10.
"""

from dataclasses import dataclass

GESAMT_ECTS = 180
ZIELNOTE_WUNSCH = 2.0
ZIELNOTE_REALISTISCH = 2.5


@dataclass
class Leistung:
    """Vereinfachte Studienleistung aus dem Entity-Modell (Phase 1)."""

    bezeichnung: str
    ects: float
    status: str  # OFFEN | IN_BEARBEITUNG | EINGEREICHT | ABGESCHLOSSEN
    benotbar: bool  # False bei Praktikum und anerkannten Leistungen
    note: float | None = None

    def ist_bewertet(self) -> bool:
        return self.note is not None

    def zaehlt_fuer_note(self) -> bool:
        return self.benotbar and self.ist_bewertet()


def beispieldaten() -> list[Leistung]:
    """Platzhalterdaten - Noten durch echte Werte ersetzen."""
    return [
        Leistung("Anerkennung Vorleistung A", 5, "ABGESCHLOSSEN", False),
        Leistung("Anerkennung Vorleistung B", 5, "ABGESCHLOSSEN", False),
        Leistung("Mathematik Grundlagen", 5, "ABGESCHLOSSEN", True, 2.3),
        Leistung("Einfuehrung Programmierung", 5, "ABGESCHLOSSEN", True, 3.0),
        Leistung("Statistik Deskriptiv", 5, "ABGESCHLOSSEN", True, 2.7),
        Leistung("Datenbankmodellierung", 5, "ABGESCHLOSSEN", True, 3.1),
        Leistung("Einfuehrung Datenschutz und IT-Sicherheit", 5, "EINGEREICHT", True),
        Leistung("Statistik - Induktive Statistik", 5, "EINGEREICHT", True),
        Leistung(
            "Praktikum: Bachelor Data Science und KI", 30, "IN_BEARBEITUNG", False
        ),
        Leistung("Projekt: Cloud Programming", 5, "IN_BEARBEITUNG", True),
    ]


def kennzahlen(leistungen: list[Leistung]) -> dict:
    """Berechnet alle Dashboard-Kennzahlen aus der Leistungsliste.

    Diese Funktion enthaelt die gesamte Fachlogik. Beide Views rufen
    sie auf und stellen das Ergebnis nur noch dar.
    """
    abgeschlossen = sum(l.ects for l in leistungen if l.status == "ABGESCHLOSSEN")
    laufend = sum(
        l.ects for l in leistungen if l.status in ("IN_BEARBEITUNG", "EINGEREICHT")
    )

    bewertete = [l for l in leistungen if l.zaehlt_fuer_note()]
    punkte = sum(l.note * l.ects for l in bewertete)
    ects_bewertet = sum(l.ects for l in bewertete)
    schnitt = punkte / ects_bewertet if ects_bewertet else None

    # Benotbare Gesamtmenge: alle ECTS ausser unbenotbaren Leistungen
    unbenotbar = sum(l.ects for l in leistungen if not l.benotbar)
    ects_benotbar_gesamt = GESAMT_ECTS - unbenotbar
    offen_benotbar = ects_benotbar_gesamt - ects_bewertet

    def restschnitt(ziel: float) -> float | None:
        if offen_benotbar <= 0:
            return None
        return (ziel * ects_benotbar_gesamt - punkte) / offen_benotbar

    return {
        "abgeschlossen": abgeschlossen,
        "laufend": laufend,
        "offen": GESAMT_ECTS - abgeschlossen - laufend,
        "fortschritt": abgeschlossen / GESAMT_ECTS,
        "schnitt": schnitt,
        "ects_bewertet": ects_bewertet,
        "ects_benotbar_gesamt": ects_benotbar_gesamt,
        "restschnitt_wunsch": restschnitt(ZIELNOTE_WUNSCH),
        "restschnitt_realistisch": restschnitt(ZIELNOTE_REALISTISCH),
    }
