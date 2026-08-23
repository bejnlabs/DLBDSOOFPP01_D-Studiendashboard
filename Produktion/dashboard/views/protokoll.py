"""Vertrag fuer die Darstellung."""

from typing import Protocol, runtime_checkable

from ..dto import DashboardDatenDTO


@runtime_checkable
class DashboardView(Protocol):
    """Eine Ansicht stellt die Kennzahlen dar.

    Bewusst auf zeige() beschraenkt: Eingabemethoden wuerden auch von
    der Kommandozeilenansicht verlangt, die nur als Rueckfallebene dient.
    """

    def zeige(self, daten: DashboardDatenDTO) -> None: ...
