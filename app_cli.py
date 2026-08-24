"""Startet das Dashboard auf der Kommandozeile.

Aufruf:  python app_cli.py [JJJJ-MM-TT]
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dashboard.app import DashboardApp
from dashboard.views import CliView


def main() -> None:
    stichtag = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else None
    DashboardApp().starte(CliView(), stichtag)


if __name__ == "__main__":
    main()
