"""
Testprogramm 3 - Berechnete Werte, Enumerationen und optionale Attribute
Gehoert zum zweiten Teil von Abschnitt 1.2 des Reflexionsdokuments.

Untersucht wird die Umsetzung abgeleiteter Attribute, die Abgrenzung
zwischen abgeleitetem Attribut und Operation, die Speicherbarkeit von
Enumerationen und der Umgang mit der Multiplizitaet [0..1].
"""

import json
from dataclasses import dataclass, field
from datetime import date
from enum import Enum

TAGE_PRO_MONAT = 30.44
GELB_AB, ROT_AB = 0.10, 0.20


class Zielstatus(str, Enum):
    GRUEN = "gruen"
    GELB = "gelb"
    ROT = "rot"

    @staticmethod
    def aus_abweichung(wert: float) -> "Zielstatus":
        if wert >= ROT_AB:
            return Zielstatus.ROT
        if wert >= GELB_AB:
            return Zielstatus.GELB
        return Zielstatus.GRUEN


class LeistungsstatusPur(Enum):
    """Reine Enumeration - nicht ohne Umwandlung speicherbar."""

    EINGEREICHT = "eingereicht"


class Leistungsstatus(str, Enum):
    """Mischform aus str und Enum - direkt nach JSON schreibbar."""

    EINGEREICHT = "eingereicht"
    ABGESCHLOSSEN = "abgeschlossen"


@dataclass
class Benotet:
    bezeichnung: str
    ects_anteil: float
    status: Leistungsstatus = Leistungsstatus.ABGESCHLOSSEN
    note: float | None = None  # Multiplizitaet [0..1]

    def ist_bewertet(self) -> bool:
        return self.note is not None

    def zaehlt_fuer_note(self) -> bool:
        return self.ist_bewertet()

    def zaehlt_fuer_tempo(self) -> bool:
        return True


@dataclass
class Studiengang:
    bezeichnung: str
    gesamt_ects: int
    startdatum: date
    leistungen: list = field(default_factory=list)

    @property
    def notendurchschnitt(self) -> float | None:
        """Abgeleitetes Attribut /notendurchschnitt."""
        relevant = [l for l in self.leistungen if l.zaehlt_fuer_note()]
        if not relevant:
            return None
        return sum(l.note * l.ects_anteil for l in relevant) / sum(
            l.ects_anteil for l in relevant
        )

    def ist_tempo(self, stichtag: date) -> float:
        """Operation - benoetigt einen Stichtag als Parameter."""
        monate = (stichtag - self.startdatum).days / TAGE_PRO_MONAT
        erbracht = sum(
            l.ects_anteil
            for l in self.leistungen
            if l.zaehlt_fuer_tempo() and l.ist_bewertet()
        )
        return erbracht / monate if monate else 0.0


print("a) Enumeration und JSON")
try:
    json.dumps({"status": LeistungsstatusPur.EINGEREICHT})
except TypeError as fehler:
    print(f"   reines Enum:  TypeError: {fehler}")
print(f"   str-Enum:     {json.dumps({'status': Leistungsstatus.EINGEREICHT})}")

print("\nb) Optionales Attribut note [0..1]")
sg = Studiengang("Angewandte Kuenstliche Intelligenz", 180, date(2025, 9, 18))
sg.leistungen = [
    Benotet("Mathematik Grundlagen", 5, note=2.3),
    Benotet("Programmierung", 5, note=3.0),
    Benotet("Induktive Statistik", 5, Leistungsstatus.EINGEREICHT),
]
for l in sg.leistungen:
    print(f"   {l.bezeichnung:24} bewertet={l.ist_bewertet()!s:5} note={l.note}")

try:
    sum(l.note * l.ects_anteil for l in sg.leistungen)
except TypeError as fehler:
    print(f"   ohne Filter:  TypeError: {fehler}")

print("\nc) Abgeleitetes Attribut und Operation")
print(f"   sg.notendurchschnitt      -> {sg.notendurchschnitt:.2f}   ohne Klammern")
print(
    f"   sg.ist_tempo(stichtag)    -> {sg.ist_tempo(date(2026, 8, 10)):.2f}   mit Klammern"
)
try:
    sg.notendurchschnitt = 1.0
except AttributeError as fehler:
    print(f"   Schreibzugriff: AttributeError: {str(fehler)[:52]}")
print("   Eine property nimmt keine Parameter entgegen. Was einen")
print("   Parameter braucht, muss als Operation umgesetzt werden.")

print("\nd) Schwellenwerte der Ampel")
for bezeichnung, ist, soll in (
    ("Terminziel", 50.0, 70.4),
    ("Notenziel 2,5", 2.78, 2.50),
    ("Tempo", 3.73, 7.79),
):
    abw = abs(ist - soll) / soll
    print(
        f"   {bezeichnung:15} Abweichung {abw:6.1%} -> "
        f"{Zielstatus.aus_abweichung(abw).value}"
    )
