"""Aufbau des Studiengangs: Studiengang, Semester und Modul."""

from dataclasses import dataclass, field
from datetime import date

from .berechnung import gewichteter_schnitt, monate_zwischen
from .enums import Leistungsstatus, Modulart
from .leistungen import Studienleistung
from .ziele import Studienziel


@dataclass(kw_only=True)
class Modul:
    """Ein Modul buendelt eine oder mehrere Studienleistungen."""

    modulnummer: str
    bezeichnung: str
    ects: int
    art: Modulart = Modulart.KURSMODUL
    leistungen: list[Studienleistung] = field(default_factory=list)

    @property
    def note(self) -> float | None:
        """Modulnote als nach ECTS-Anteilen gewichtetes Mittel.

        Beruecksichtigt werden ausschliesslich bewertete, benotete
        Leistungen. Besteht ein Modul aus mehreren Leistungen, etwa das
        Abschlussmodul aus Bachelorarbeit (9 ECTS) und Kolloquium
        (1 ECTS), ergibt sich die Modulnote aus deren Gewichtung. Liegt
        keine bewertete Leistung vor, wird None zurueckgegeben.

        Der Wert dient der Anzeige. Der Notendurchschnitt des
        Studiengangs wird bewusst nicht ueber die Modulnoten, sondern
        direkt ueber die Leistungen berechnet, damit keine
        Rundungskette entsteht.
        """
        return gewichteter_schnitt(
            [(l.note, l.ects_anteil) for l in self.leistungen
             if l.zaehlt_fuer_note()])

    @property
    def ist_bestanden(self) -> bool:
        return bool(self.leistungen) and all(
            l.ist_bestanden() for l in self.leistungen)

    @property
    def status(self) -> Leistungsstatus:
        """Fortgeschrittenster Status der enthaltenen Leistungen."""
        rang = list(Leistungsstatus)
        if not self.leistungen:
            return Leistungsstatus.OFFEN
        return max((l.status for l in self.leistungen), key=rang.index)


@dataclass(kw_only=True)
class Semester:
    """Ein Semester ordnet bestehende Module zeitlich zu (Aggregation)."""

    nummer: int
    startdatum: date | None = None
    module: list[Modul] = field(default_factory=list)

    def ordne_zu(self, modul: Modul) -> None:
        if modul not in self.module:
            self.module.append(modul)

    def entferne(self, modul: Modul) -> None:
        """Loest nur die Zuordnung. Das Modul bleibt im Katalog bestehen."""
        if modul in self.module:
            self.module.remove(modul)


@dataclass(kw_only=True)
class Studiengang:
    """Wurzel des Modells.

    Der Studiengang haelt den Modulkatalog sowie die Semester. Die
    Semester verweisen auf Module dieses Katalogs, weshalb ein Modul
    auch ohne Semesterzuordnung bestehen kann.
    """

    bezeichnung: str
    gesamt_ects: int
    startdatum: date
    regelenddatum: date
    module: list[Modul] = field(default_factory=list)
    semester: list[Semester] = field(default_factory=list)
    ziele: list[Studienziel] = field(default_factory=list)

    @property
    def alle_leistungen(self) -> list[Studienleistung]:
        return [l for m in self.module for l in m.leistungen]

    @property
    def erreichte_ects(self) -> float:
        """Summe der ECTS-Punkte aus bestandenen Leistungen."""
        return sum(l.ects_anteil for l in self.alle_leistungen
                   if l.ist_bestanden())

    @property
    def selbst_erbrachte_ects(self) -> float:
        """Bestandene ECTS-Punkte ohne anerkannte Vorleistungen."""
        return sum(l.ects_anteil for l in self.alle_leistungen
                   if l.ist_bestanden() and l.zaehlt_fuer_tempo())

    @property
    def notendurchschnitt(self) -> float | None:
        """Nach ECTS-Punkten gewichteter Durchschnitt.

        Einzige fachliche Quelle des Notendurchschnitts. Die Berechnung
        erfolgt direkt ueber die Leistungen und nicht ueber die
        Modulnoten.
        """
        return gewichteter_schnitt(
            [(l.note, l.ects_anteil) for l in self.alle_leistungen
             if l.zaehlt_fuer_note()])

    @property
    def bewertete_ects(self) -> float:
        return sum(l.ects_anteil for l in self.alle_leistungen
                   if l.zaehlt_fuer_note())

    @property
    def benotbare_ects(self) -> float:
        """Gesamtmenge der ECTS-Punkte, die in die Note eingehen koennen."""
        nicht_benotbar = sum(l.ects_anteil for l in self.alle_leistungen
                             if not l.ist_benotbar())
        return self.gesamt_ects - nicht_benotbar

    def ist_tempo(self, stichtag: date) -> float:
        """Bisher erreichtes Arbeitstempo in ECTS-Punkten pro Monat."""
        monate = monate_zwischen(self.startdatum, stichtag)
        return self.selbst_erbrachte_ects / monate if monate > 0 else 0.0
