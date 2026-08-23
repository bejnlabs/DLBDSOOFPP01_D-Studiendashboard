"""Hierarchie der Studienleistungen.

Die Hierarchie ist zweistufig aufgebaut. Die erste Ebene unterscheidet
nach der Art des Erwerbs (Pruefung oder Anerkennung), die zweite nach
der Art der Bewertung (benotet oder unbenotet).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

from .enums import Leistungsstatus, Pruefungsform

BESTEHENSGRENZE = 4.0


@dataclass(kw_only=True)
class Studienleistung(ABC):
    """Abstrakte Oberklasse aller Leistungen, die ECTS-Punkte einbringen.

    kw_only ist erforderlich, weil Unterklassen Pflichtfelder ergaenzen,
    waehrend status bereits einen Standardwert besitzt.
    """

    bezeichnung: str
    ects_anteil: float
    status: Leistungsstatus = Leistungsstatus.OFFEN

    @abstractmethod
    def ist_bestanden(self) -> bool:
        """Gibt an, ob die Leistung erfolgreich abgeschlossen wurde."""

    @abstractmethod
    def zaehlt_fuer_note(self) -> bool:
        """Gibt an, ob die Leistung in den Notendurchschnitt eingeht."""

    @abstractmethod
    def zaehlt_fuer_tempo(self) -> bool:
        """Gibt an, ob die Leistung als selbst erbracht gilt.

        Anerkannte Leistungen wurden nicht ueber Zeit erarbeitet und
        duerfen das Arbeitstempo daher nicht erhoehen.
        """

    @abstractmethod
    def ist_benotbar(self) -> bool:
        """Gibt an, ob die Leistung grundsaetzlich benotet wird.

        Unterscheidet sich von zaehlt_fuer_note(): Eine eingereichte,
        noch unbewertete Leistung ist benotbar, zaehlt aber noch nicht.
        """


@dataclass(kw_only=True)
class Pruefungsleistung(Studienleistung, ABC):
    """Leistung, die durch eine Pruefung erbracht wird."""

    form: Pruefungsform
    versuch: int = 1
    pruefungsdatum: date | None = None

    def zaehlt_fuer_tempo(self) -> bool:
        return True


@dataclass(kw_only=True)
class Benotet(Pruefungsleistung):
    """Pruefungsleistung mit Note.

    Die Note ist optional, da eine eingereichte Leistung noch nicht
    bewertet sein kann (Multiplizitaet [0..1] im Klassendiagramm).
    """

    note: float | None = None

    def ist_bewertet(self) -> bool:
        return self.note is not None

    def ist_bestanden(self) -> bool:
        return self.ist_bewertet() and self.note <= BESTEHENSGRENZE

    def zaehlt_fuer_note(self) -> bool:
        return self.ist_bewertet()

    def ist_benotbar(self) -> bool:
        return True


@dataclass(kw_only=True)
class Unbenotet(Pruefungsleistung):
    """Pruefungsleistung, die nur bestanden oder nicht bestanden wird."""

    bestanden: bool = False

    def ist_bestanden(self) -> bool:
        return self.bestanden

    def zaehlt_fuer_note(self) -> bool:
        return False

    def ist_benotbar(self) -> bool:
        return False


@dataclass(kw_only=True)
class AnerkannteLeistung(Studienleistung):
    """Uebertragene Vorleistung ohne eigene Pruefung."""

    herkunft: str
    anerkennungsdatum: date | None = None

    def ist_bestanden(self) -> bool:
        return True

    def zaehlt_fuer_note(self) -> bool:
        return False

    def zaehlt_fuer_tempo(self) -> bool:
        return False

    def ist_benotbar(self) -> bool:
        return False
