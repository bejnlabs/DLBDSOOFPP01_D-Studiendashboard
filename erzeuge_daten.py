"""Erzeugt die Studiendaten aus dem Studienablaufplan.

Grundlage ist der Studienablaufplan B.Sc. Angewandte Kuenstliche
Intelligenz (Teilzeit I). Die Kurscodes werden als Modulnummern
uebernommen. Die Semester sind nach dem tatsaechlichen
Bearbeitungsverlauf zugeordnet; noch nicht begonnene Module besitzen
keine Semesterzuordnung und belegen damit die Multiplizitaet 0..1
zwischen Semester und Modul.
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dashboard.domaene import (
    AnerkannteLeistung,
    Benotet,
    Leistungsstatus,
    Modul,
    Modulart,
    Notenziel,
    Pruefungsform,
    Semester,
    Studiengang,
    Terminziel,
    Unbenotet,
)
from dashboard.repository import JsonStudiengangRepository

AB, IB, EI, OF = (
    Leistungsstatus.ABGESCHLOSSEN,
    Leistungsstatus.IN_BEARBEITUNG,
    Leistungsstatus.EINGEREICHT,
    Leistungsstatus.OFFEN,
)
PR, AW, PO = (
    Pruefungsform.PRUEFUNG,
    Pruefungsform.ADVANCED_WORKBOOK,
    Pruefungsform.PORTFOLIO,
)
FA, FP, PB = (
    Pruefungsform.FALLSTUDIE,
    Pruefungsform.FACHPRAESENTATION,
    Pruefungsform.PROJEKTBERICHT,
)

# ------------------------------------------------- anerkannte Vorleistungen
ANERKANNT = [
    ("DLBSG1", "Studium Generale I"),
    ("DLBSG2", "Studium Generale II"),
]

# ------------------------------------------------------ bewertete Leistungen
BEWERTET = [
    ("DLBDSEAIS01-01_D", "Artificial Intelligence", PR, 3.3),
    ("DLBBIMD01", "Mathematik: Analysis", PR, 3.3),
    ("DLBBIM01", "Mathematik: Lineare Algebra", PR, 2.3),
    (
        "DLBWIRITT01",
        "Einführung in das wissenschaftliche Arbeiten fuer IT und Technik",
        AW,
        1.3,
    ),
    (
        "DLBDSSPDS01_D",
        "Statistik - Wahrscheinlichkeit und deskriptive Statistik",
        AW,
        3.7,
    ),
    ("DLBDSIPWP01_D", "Einführung in die Programmierung mit Python", PR, 2.0),
    ("DLBDSCC01_D", "Cloud Computing", PR, 3.0),
    ("IAMG01", "IT-Architekturmanagement", PR, 3.3),
    ("DLBISIC01", "Einführung in Datenschutz und IT-Sicherheit", PR, 3.3),
]

# --------------------------------------------------------------- eingereicht
EINGEREICHT = [
    ("IDBS01", "Datenmodellierung und Datenbanksysteme", PR),
    ("DLBDSSIS01_D", "Statistik - Induktive Statistik", PR),
    ("IWBI01", "Business Intelligence", PR),
    (
        "DLBDSOOFPP01_D",
        "Projekt: Objektorientierte und funktionale Programmierung mit Python",
        PO,
    ),
]

# ----------------------------------------------------------- in Bearbeitung
IN_BEARBEITUNG = [
    ("DLBSEPCP01_D", "Projekt: Cloud Programming", PO),
]

# ----------------------------------------------------------- offene Module
OFFEN = [
    ("DLBDSMLSL01_D", "Maschinelles Lernen - Supervised Learning", PR),
    (
        "DLBDSMLUSL01_D",
        "Maschinelles Lernen - Unsupervised Learning und Feature Engineering",
        FA,
    ),
    ("DLBDSNNDL01-01_D", "Neuronale Netze und Deep Learning", FP),
    ("DLBAIICV01_D", "Einführung in Computer Vision", PR),
    ("DLBAIPCV01_D", "Projekt: Computer Vision", PB),
    ("DLBAIIRL01_D", "Einführung in das Reinforcement Learning", PR),
    ("DLBAIBEELAAI01_D", "Ethische und rechtliche Aspekte in der KI", PR),
    ("DLBAIINLP01_D", "Einführung in NLP", PR),
    ("DLBAIPNLP01_D", "Projekt: NLP", PB),
    ("DLBAIBESEI01_D", "Seminar: Ethische Innovation", Pruefungsform.SEMINARARBEIT),
    ("DLBAIPEAI01_D", "Projekt: Edge AI", PB),
    ("DLBDSME01_D", "Model Engineering", FA),
]


def kursmodul(nummer, bezeichnung, form, status, note=None):
    return Modul(
        modulnummer=nummer,
        bezeichnung=bezeichnung,
        ects=5,
        art=Modulart.KURSMODUL,
        leistungen=[
            Benotet(
                bezeichnung=bezeichnung,
                ects_anteil=5,
                status=status,
                form=form,
                note=note,
            )
        ],
    )


module = []

for nummer, bezeichnung in ANERKANNT:
    module.append(
        Modul(
            modulnummer=nummer,
            bezeichnung=bezeichnung,
            ects=5,
            leistungen=[
                AnerkannteLeistung(
                    bezeichnung=bezeichnung,
                    ects_anteil=5,
                    status=AB,
                    herkunft="Anerkennung",
                    anerkennungsdatum=date(2025, 10, 1),
                )
            ],
        )
    )

for nummer, bezeichnung, form, note in BEWERTET:
    module.append(kursmodul(nummer, bezeichnung, form, AB, note))

for nummer, bezeichnung, form in EINGEREICHT:
    module.append(kursmodul(nummer, bezeichnung, form, EI))

for nummer, bezeichnung, form in IN_BEARBEITUNG:
    module.append(kursmodul(nummer, bezeichnung, form, IB))

# Wahlpflichtbereich D: Praktikum mit 30 ECTS und einer Praxisreflexion
module.append(
    Modul(
        modulnummer="DLBDSCIBDSC01-01_D",
        bezeichnung="Praktikum: Bachelor Data Science und KI",
        ects=30,
        art=Modulart.PRAKTIKUM,
        leistungen=[
            Unbenotet(
                bezeichnung="Praxisreflexion",
                ects_anteil=30,
                status=IB,
                form=Pruefungsform.PRAXISREFLEXION,
                bestanden=False,
            )
        ],
    )
)

for nummer, bezeichnung, form in OFFEN:
    module.append(kursmodul(nummer, bezeichnung, form, OF))

# Abschlussmodul aus zwei Leistungen mit unterschiedlicher Gewichtung
module.append(
    Modul(
        modulnummer="BBAK",
        bezeichnung="Abschlussmodul",
        ects=10,
        art=Modulart.ABSCHLUSSMODUL,
        leistungen=[
            Benotet(
                bezeichnung="Bachelorarbeit",
                ects_anteil=9,
                status=OF,
                form=Pruefungsform.BACHELORARBEIT,
                note=None,
            ),
            Benotet(
                bezeichnung="Kolloquium",
                ects_anteil=1,
                status=OF,
                form=Pruefungsform.KOLLOQUIUM,
                note=None,
            ),
        ],
    )
)

nach_nummer = {m.modulnummer: m for m in module}

# Semesterstruktur des Modells Teilzeit I: acht Semester zu je sechs
# Monaten. Die Semester 1 und 2 bilden den tatsaechlichen Verlauf ab,
# die Semester 3 bis 8 die Planung bis zum Ende der Regelstudienzeit.
SEMESTERSTART = [
    date(2025, 9, 18),
    date(2026, 3, 18),
    date(2026, 9, 18),
    date(2027, 3, 18),
    date(2027, 9, 18),
    date(2028, 3, 18),
    date(2028, 9, 18),
    date(2029, 3, 18),
]

ZUORDNUNG = {
    1: [n for n, *_ in ANERKANNT] + [n for n, *_ in BEWERTET[:5]],
    2: [n for n, *_ in BEWERTET[5:]]
    + [n for n, *_ in EINGEREICHT]
    + [n for n, *_ in IN_BEARBEITUNG]
    + ["DLBDSCIBDSC01-01_D"],
    3: ["DLBDSMLSL01_D", "DLBDSMLUSL01_D", "DLBDSNNDL01-01_D"],
    4: ["DLBAIICV01_D", "DLBAIPCV01_D", "DLBAIIRL01_D"],
    5: ["DLBAIBEELAAI01_D", "DLBAIINLP01_D"],
    6: ["DLBAIPNLP01_D", "DLBAIBESEI01_D"],
    7: ["DLBAIPEAI01_D", "DLBDSME01_D"],
    8: ["BBAK"],
}

semester = [
    Semester(
        nummer=nr,
        startdatum=SEMESTERSTART[nr - 1],
        module=[nach_nummer[n] for n in ZUORDNUNG[nr]],
    )
    for nr in sorted(ZUORDNUNG)
]

studiengang = Studiengang(
    bezeichnung="Angewandte Künstliche Intelligenz (B.Sc.), Teilzeit I",
    gesamt_ects=180,
    startdatum=date(2025, 9, 18),
    regelenddatum=date(2029, 8, 15),
    module=module,
    semester=semester,
    ziele=[
        Terminziel(bezeichnung="Zielbild", zieldatum=date(2027, 12, 31)),
        Notenziel(bezeichnung="Wunschziel", zielnote=2.0),
        Notenziel(bezeichnung="Realistisches Ziel", zielnote=2.5),
    ],
)

JsonStudiengangRepository("daten/studiengang.json").speichern(studiengang)

zugeordnet = {m.modulnummer for s in semester for m in s.module}
print(f"{len(module)} Module, {sum(m.ects for m in module)} ECTS")
print(
    f"Semester: {len(semester)}, zugeordnete Module: {len(zugeordnet)}, "
    f"ohne Zuordnung: {len(module) - len(zugeordnet)}"
)
for s in semester:
    ects = sum(m.ects for m in s.module)
    print(
        f"  Semester {s.nummer} ab {s.startdatum:%d.%m.%Y}: "
        f"{len(s.module)} Module, {ects:>2} ECTS"
    )
print(f"erreichte ECTS    : {studiengang.erreichte_ects}")
print(f"selbst erbracht   : {studiengang.selbst_erbrachte_ects}")
print(f"bewertete ECTS    : {studiengang.bewertete_ects}")
print(f"benotbare ECTS    : {studiengang.benotbare_ects}")
print(f"Notendurchschnitt : {studiengang.notendurchschnitt:.4f}")
