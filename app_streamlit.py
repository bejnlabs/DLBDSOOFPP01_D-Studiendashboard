"""Startet das Dashboard im Browser.

Aufruf:  python -m streamlit run app_streamlit.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dashboard.app import DashboardApp
from dashboard.views.streamlit_view import StreamlitView

anwendung = DashboardApp()
anwendung.starte(StreamlitView(controller=anwendung.controller))
