"""Berechnung der Kennzahlen.

Die Dienste ermitteln Vorausberechnungen und Vergleiche mit Zielwerten.
Der gegenwaertige Zustand des Studiengangs wird dagegen von den
Domaenenklassen selbst geliefert; der Notendurchschnitt etwa steht
ausschliesslich als Eigenschaft am Studiengang.
"""

from datetime import date

from .domaene import (Leistungsstatus, Notenziel, Studiengang, Terminziel,
                      Zielstatus, monate_zwischen, soll_ects_linear)

BESTNOTE = 1.0
SCHLECHTESTE_BESTANDENE_NOTE = 4.0


class FortschrittService:
    """Kennzahlen zu Studienfortschritt und Arbeitstempo."""

    def ects_nach_status(self, sg: Studiengang) -> dict[Leistungsstatus, float]:
        """Verteilung der ECTS-Punkte auf die Bearbeitungsstaende."""
        verteilung = {status: 0.0 for status in Leistungsstatus}
        for leistung in sg.alle_leistungen:
            verteilung[leistung.status] += leistung.ects_anteil
        return verteilung

    def soll_ects(self, sg: Studiengang, bezugsdatum: date,
                  stichtag: date) -> float:
        return soll_ects_linear(sg.gesamt_ects, sg.startdatum,
                                bezugsdatum, stichtag)

    def soll_tempo(self, sg: Studiengang, bezugsdatum: date,
                   stichtag: date) -> float:
        """Erforderliches Tempo bis zum Bezugsdatum in ECTS pro Monat."""
        rest = max(0.0, sg.gesamt_ects - sg.erreichte_ects)
        monate = monate_zwischen(stichtag, bezugsdatum)
        return rest / monate if monate > 0 else float("inf")

    def tempo_abweichung(self, sg: Studiengang, bezugsdatum: date,
                         stichtag: date) -> float:
        """Richtungsabhaengige Abweichung des Arbeitstempos.

        Gewertet wird nur ein Zurueckbleiben hinter dem Sollwert. Liegt
        das Ist-Tempo darueber, ergibt sich 0.0.
        """
        soll = self.soll_tempo(sg, bezugsdatum, stichtag)
        if soll <= 0 or soll == float("inf"):
            return 0.0
        return max(0.0, (soll - sg.ist_tempo(stichtag)) / soll)

    def tempo_status(self, sg: Studiengang, bezugsdatum: date,
                     stichtag: date) -> Zielstatus:
        return Zielstatus.aus_abweichung(
            self.tempo_abweichung(sg, bezugsdatum, stichtag))


class NotenService:
    """Vorausberechnungen zum Notendurchschnitt.

    Der aktuelle Durchschnitt wird nicht hier, sondern von
    Studiengang.notendurchschnitt geliefert.
    """

    def restschnitt(self, sg: Studiengang, ziel: Notenziel) -> float | None:
        """Erforderlicher Durchschnitt der verbleibenden Leistungen.

        Ergibt sich aus dem Notenpunktebudget der Zielnote abzueglich
        der bereits verbrauchten Punkte, verteilt auf die noch offenen
        benotbaren ECTS-Punkte.
        """
        offen = sg.benotbare_ects - sg.bewertete_ects
        if offen <= 0:
            return None
        schnitt = sg.notendurchschnitt or 0.0
        verbraucht = schnitt * sg.bewertete_ects
        budget = ziel.zielnote * sg.benotbare_ects
        return (budget - verbraucht) / offen

    def korridor(self, sg: Studiengang) -> tuple[float, float] | None:
        """Bestenfalls und schlechtestenfalls erreichbare Abschlussnote."""
        if sg.bewertete_ects <= 0:
            return None
        offen = sg.benotbare_ects - sg.bewertete_ects
        verbraucht = (sg.notendurchschnitt or 0.0) * sg.bewertete_ects
        bester = (verbraucht + BESTNOTE * offen) / sg.benotbare_ects
        schlechtester = ((verbraucht + SCHLECHTESTE_BESTANDENE_NOTE * offen)
                         / sg.benotbare_ects)
        return (bester, schlechtester)
