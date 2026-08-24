"""Datenobjekte fuer die Uebergabe an die Darstellung.

Data Transfer Objects enthalten ausschliesslich Werte und keine Logik.
Sie ersetzen die Woerterbuecher aus der Machbarkeitspruefung, weil ihre
Felder festgelegt sind und Tippfehler dadurch frueher auffallen.
"""

from dataclasses import dataclass, field
from datetime import date

from .domaene import Leistungsstatus, Pruefungsform, Zielstatus


@dataclass(kw_only=True)
class ZielwertDTO:
    """Ein Zielwert mit dem zugehoerigen Sollstand."""

    bezeichnung: str
    zielwert: float
    sollwert: float
    abweichung: float
    status: Zielstatus


@dataclass(kw_only=True)
class FortschrittKachelDTO:
    gesamt_ects: int
    erreichte_ects: float
    ects_nach_status: dict[Leistungsstatus, float]
    soll_ects_zielbild: float
    soll_ects_regelende: float
    abweichung_ects: float
    vorsprung_regelende: float
    status: Zielstatus


@dataclass(kw_only=True)
class NotenKachelDTO:
    durchschnitt: float | None
    bewertete_ects: float
    benotbare_ects: float
    korridor: tuple[float, float] | None
    ziele: list[ZielwertDTO] = field(default_factory=list)
    restschnitt_je_ziel: dict[str, float | None] = field(default_factory=dict)
    status: Zielstatus = Zielstatus.GRUEN


@dataclass(kw_only=True)
class TempoKachelDTO:
    ist_tempo: float
    soll_tempo_zielbild: float
    soll_tempo_regelende: float
    abweichung: float
    status: Zielstatus


@dataclass(kw_only=True)
class LeistungszeileDTO:
    """Einzelne Studienleistung eines Moduls.

    Ermoeglicht der Darstellung, eine Leistung zur Auswahl anzubieten,
    ohne dass Domaenenobjekte die Schichtgrenze ueberschreiten.
    """

    bezeichnung: str
    ects_anteil: float
    form: Pruefungsform | None
    status: Leistungsstatus
    note: float | None
    benotbar: bool


@dataclass(kw_only=True)
class ModulzeileDTO:
    modulnummer: str
    bezeichnung: str
    ects: int
    status: Leistungsstatus
    note: float | None
    leistungen: list[LeistungszeileDTO] = field(default_factory=list)


@dataclass(kw_only=True)
class DashboardDatenDTO:
    stichtag: date
    studiengang: str
    fortschritt: FortschrittKachelDTO
    noten: NotenKachelDTO
    tempo: TempoKachelDTO
    laufende_module: list[ModulzeileDTO] = field(default_factory=list)
    alle_module: list[ModulzeileDTO] = field(default_factory=list)
