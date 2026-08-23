"""
Testprogramm 1 - Klassen, Vererbung und Abstraktion
Gehoert zu Abschnitt 1.1 des Reflexionsdokuments.

Untersucht wird, ob sich die dreistufige Leistungshierarchie des
Konzeptdiagramms mit @dataclass abbilden laesst und welche
Moeglichkeiten Python fuer abstrakte Klassen bietet.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, runtime_checkable


class Leistungsstatus(str, Enum):
    OFFEN = "offen"
    ABGESCHLOSSEN = "abgeschlossen"


print("a) Veraenderliche Standardwerte")


@dataclass
class Modul:
    bezeichnung: str
    leistungen: list = field(default_factory=list)


a, b = Modul("Modul A"), Modul("Modul B")
a.leistungen.append("Portfolio")
print(
    f"   A={a.leistungen}  B={b.leistungen}  getrennt={a.leistungen is not b.leistungen}"
)


print("\nb) Vererbung mit @dataclass")


@dataclass
class StudienleistungNaiv:
    bezeichnung: str
    status: Leistungsstatus = Leistungsstatus.OFFEN


try:

    @dataclass
    class UnbenotetNaiv(StudienleistungNaiv):
        bestanden: bool  # Pflichtfeld nach Feld mit Standardwert

    print("   unerwartet erfolgreich")
except TypeError as fehler:
    print(f"   TypeError: {fehler}")


@dataclass(kw_only=True)
class Studienleistung(ABC):
    bezeichnung: str
    ects_anteil: float
    status: Leistungsstatus = Leistungsstatus.OFFEN

    @abstractmethod
    def ist_bestanden(self) -> bool: ...

    @abstractmethod
    def zaehlt_fuer_note(self) -> bool: ...

    @abstractmethod
    def zaehlt_fuer_tempo(self) -> bool: ...


@dataclass(kw_only=True)
class Unbenotet(Studienleistung):
    bestanden: bool

    def ist_bestanden(self) -> bool:
        return self.bestanden

    def zaehlt_fuer_note(self) -> bool:
        return False

    def zaehlt_fuer_tempo(self) -> bool:
        return True


@dataclass(kw_only=True)
class AnerkannteLeistung(Studienleistung):
    herkunft: str

    def ist_bestanden(self) -> bool:
        return True

    def zaehlt_fuer_note(self) -> bool:
        return False

    def zaehlt_fuer_tempo(self) -> bool:
        return False


praktikum = Unbenotet(bezeichnung="Praxisreflexion", ects_anteil=30, bestanden=False)
print(f"   mit kw_only=True erzeugbar: {praktikum.bezeichnung}")


print("\nc) Abstraktion mit ABC")
try:
    Studienleistung(bezeichnung="X", ects_anteil=5)
except TypeError as fehler:
    print(f"   TypeError: {str(fehler)[:70]}")

anerkennung = AnerkannteLeistung(
    bezeichnung="Vorleistung", ects_anteil=5, herkunft="Vorstudium"
)
for leistung in (praktikum, anerkennung):
    print(
        f"   {type(leistung).__name__:20} note={leistung.zaehlt_fuer_note()!s:5} "
        f"tempo={leistung.zaehlt_fuer_tempo()}"
    )


print("\nd) Abstraktion mit Protocol")


@runtime_checkable
class DashboardView(Protocol):
    def zeige(self, daten: dict) -> None: ...


class CliView:  # erbt NICHT von DashboardView
    def zeige(self, daten: dict) -> None:
        print(f"   CLI: Fortschritt {daten['fortschritt']:.1%}")


class FalscheView:
    def anzeigen(self, daten: dict) -> None: ...


for kandidat in (CliView(), FalscheView()):
    passt = isinstance(kandidat, DashboardView)
    print(f"   {type(kandidat).__name__:14} erfuellt Vertrag: {passt}")
    if passt:
        kandidat.zeige({"fortschritt": 0.278})
