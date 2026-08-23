"""Gemeinsame Berechnungsregeln der Domaene."""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

TAGE_PRO_MONAT = 30.44


def monate_zwischen(von: date, bis: date) -> float:
    """Zeitspanne in Monaten. Negative Spannen werden zu 0.0."""
    return max(0.0, (bis - von).days / TAGE_PRO_MONAT)


def soll_ects_linear(gesamt_ects: int, startdatum: date,
                     bezugsdatum: date, stichtag: date) -> float:
    """Soll-Stand der ECTS-Punkte bei gleichmaessiger Verteilung.

    Wird sowohl vom Terminziel als auch vom FortschrittService benoetigt
    und ist deshalb hier einmalig hinterlegt.
    """
    gesamtdauer = (bezugsdatum - startdatum).days
    if gesamtdauer <= 0:
        return float(gesamt_ects)
    vergangen = max(0, (stichtag - startdatum).days)
    return min(float(gesamt_ects), gesamt_ects * vergangen / gesamtdauer)


def gewichteter_schnitt(paare: list[tuple[float, float]]) -> float | None:
    """Nach ECTS-Punkten gewichteter Notendurchschnitt.

    paare enthaelt Tupel aus (Note, ECTS-Anteil). Liegt keine bewertete
    Leistung vor, wird None zurueckgegeben.
    """
    if not paare:
        return None
    gewicht = sum(ects for _, ects in paare)
    if gewicht == 0:
        return None
    return sum(note * ects for note, ects in paare) / gewicht


def runde(wert: float | None, stellen: int = 2) -> float | None:
    """Kaufmaennische Rundung.

    Die in Python uebliche Rundung zur naechsten geraden Ziffer wuerde
    einen Notendurchschnitt von 2,775 zu 2,77 runden. Fuer die Anzeige
    von Noten ist das kaufmaennische Aufrunden zu 2,78 gebraeuchlich.
    """
    if wert is None:
        return None
    muster = Decimal(1).scaleb(-stellen)
    return float(Decimal(str(wert)).quantize(muster, rounding=ROUND_HALF_UP))
