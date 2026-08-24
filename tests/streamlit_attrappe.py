"""Minimale Attrappe der Streamlit-Schnittstelle.

Ermoeglicht es, die Streamlit-Ansicht in den automatisierten Tests
auszufuehren, ohne die Bibliothek zu installieren. Alle Aufrufe werden
lediglich mitgeschrieben.
"""

import sys
import types

aufrufe: list[str] = []


def _merken(name):
    def platzhalter(*args, **kwargs):
        aufrufe.append(name)
        if name == "selectbox":
            werte = list(args[1]) if len(args) > 1 else []
            index = kwargs.get("index", 0)
            if kwargs.get("format_func") and werte:
                kwargs["format_func"](werte[index])
            return werte[index] if werte else None
        if name in ("checkbox", "button", "form_submit_button"):
            return False
        return None
    return platzhalter


class _Spalte:
    def __getattr__(self, name):
        return _merken(f"spalte.{name}")


class _Formular:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def _columns(anzahl, *a, **k):
    aufrufe.append("columns")
    return [_Spalte() for _ in range(anzahl if isinstance(anzahl, int)
                                     else len(anzahl))]


def installieren() -> types.ModuleType:
    modul = types.ModuleType("streamlit")
    for name in ("title", "caption", "subheader", "write", "markdown",
                 "progress", "divider", "info", "success", "error",
                 "warning", "dataframe", "set_page_config", "rerun",
                 "selectbox", "checkbox", "button", "form_submit_button",
                 "number_input", "text_input", "metric"):
        setattr(modul, name, _merken(name))
    modul.columns = _columns
    modul.form = lambda *a, **k: _Formular()
    modul.expander = lambda *a, **k: _Formular()
    modul.column_config = types.SimpleNamespace()
    sys.modules["streamlit"] = modul
    return modul
