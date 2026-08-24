"""Studienziele des Dashboards.

Die abstrakte Oberklasse legt fest, wie aus einer Abweichung eine
Ampelfarbe wird. Die Unterklassen bestimmen lediglich, wie die
Abweichung fuer ihre Zielart gebildet wird.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

from .berechnung import soll_ects_linear
from .enums import Zielstatus


@dataclass(kw_only=True)
class Studienziel(ABC):
    """Abstraktes Ziel, dessen Erreichung ueberwacht wird."""

    bezeichnung: str

    @abstractmethod
    def abweichung(self, studiengang, stichtag: date) -> float:
        """Richtungsabhaengige Abweichung vom Sollwert.

        Der Wert ist nie negativ: Wird das Ziel uebertroffen, ergibt
        sich 0.0. Nur ein Zurueckbleiben beziehungsweise eine
        Ueberschreitung wird als Abweichung gewertet.
        """

    @abstractmethod
    def zielerreichungsgrad(self, studiengang, stichtag: date) -> float:
        """Verhaeltnis von Ist- zu Sollwert."""

    def status(self, studiengang, stichtag: date) -> Zielstatus:
        """Ampelfarbe des Ziels. Fuer alle Zielarten identisch."""
        return Zielstatus.aus_abweichung(self.abweichung(studiengang, stichtag))


@dataclass(kw_only=True)
class Terminziel(Studienziel):
    """Ziel fuer den Abschluss zu einem bestimmten Datum."""

    zieldatum: date

    def soll_ects(self, studiengang, stichtag: date) -> float:
        return soll_ects_linear(studiengang.gesamt_ects,
                                studiengang.startdatum,
                                self.zieldatum, stichtag)

    def abweichung(self, studiengang, stichtag: date) -> float:
        soll = self.soll_ects(studiengang, stichtag)
        if soll <= 0:
            return 0.0
        # Nur ein Rueckstand zaehlt, ein Vorsprung ergibt 0.0
        return max(0.0, (soll - studiengang.erreichte_ects) / soll)

    def zielerreichungsgrad(self, studiengang, stichtag: date) -> float:
        soll = self.soll_ects(studiengang, stichtag)
        return studiengang.erreichte_ects / soll if soll > 0 else 1.0


@dataclass(kw_only=True)
class Notenziel(Studienziel):
    """Ziel fuer den angestrebten Notendurchschnitt."""

    zielnote: float

    def abweichung(self, studiengang, stichtag: date | None = None) -> float:
        ist = studiengang.notendurchschnitt
        if ist is None or self.zielnote <= 0:
            return 0.0
        # Bei Noten ist ein kleinerer Wert besser, daher zaehlt nur
        # eine Ueberschreitung des Zielwerts als Abweichung.
        return max(0.0, (ist - self.zielnote) / self.zielnote)

    def zielerreichungsgrad(self, studiengang, stichtag: date | None = None) -> float:
        ist = studiengang.notendurchschnitt
        if ist is None or ist <= 0:
            return 1.0
        return self.zielnote / ist

    def status(self, studiengang, stichtag: date | None = None) -> Zielstatus:
        return Zielstatus.aus_abweichung(self.abweichung(studiengang, stichtag))
