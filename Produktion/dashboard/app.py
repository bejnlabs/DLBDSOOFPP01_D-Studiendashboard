"""Erzeugt die Objekte und verbindet sie miteinander.

Welche Ansicht verwendet wird, erhaelt die Anwendung von aussen. Dadurch
sind Kommandozeile und Streamlit austauschbar, ohne dass an der
Berechnung etwas geaendert werden muss.
"""

from datetime import date
from pathlib import Path

from .controller import DashboardController
from .repository import JsonStudiengangRepository
from .services import FortschrittService, NotenService
from .views.protokoll import DashboardView

STANDARDPFAD = Path(__file__).resolve().parent.parent / "daten" / "studiengang.json"


class DashboardApp:
    def __init__(self, datenpfad: Path | str = STANDARDPFAD) -> None:
        self.controller = DashboardController(
            repository=JsonStudiengangRepository(datenpfad),
            fortschritt=FortschrittService(), noten=NotenService())

    def starte(self, view: DashboardView, stichtag: date | None = None) -> None:
        view.zeige(self.controller.lade_daten(stichtag))
