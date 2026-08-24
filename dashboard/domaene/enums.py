"""Aufzaehlungstypen der Domaene.

Alle Enumerationen sind als Mischform aus str und Enum umgesetzt, damit
sie ohne zusaetzliche Umwandlung im JSON-Format gespeichert werden koennen.
"""

from enum import Enum

# Schwellenwerte der Ampelanzeige (Abweichung vom jeweiligen Sollwert)
GELB_AB = 0.10
ROT_AB = 0.20


class Modulart(str, Enum):
    KURSMODUL = "Kursmodul"
    PRAKTIKUM = "Praktikum"
    ABSCHLUSSMODUL = "Abschlussmodul"


class Pruefungsform(str, Enum):
    PRUEFUNG = "Pruefung"
    ADVANCED_WORKBOOK = "Advanced Workbook"
    PORTFOLIO = "Portfolio"
    FALLSTUDIE = "Fallstudie"
    FACHPRAESENTATION = "Fachpraesentation"
    PROJEKTBERICHT = "Projektbericht"
    PRAXISREFLEXION = "Praxisreflexion"
    SEMINARARBEIT = "Seminararbeit"
    BACHELORARBEIT = "Bachelorarbeit"
    KOLLOQUIUM = "Kolloquium"


class Leistungsstatus(str, Enum):
    OFFEN = "offen"
    IN_BEARBEITUNG = "in Bearbeitung"
    EINGEREICHT = "eingereicht"
    ABGESCHLOSSEN = "abgeschlossen"


class Zielstatus(str, Enum):
    """Ampelanzeige eines Ziels."""

    GRUEN = "gruen"
    GELB = "gelb"
    ROT = "rot"

    @staticmethod
    def aus_abweichung(abweichung: float) -> "Zielstatus":
        """Ordnet einer Abweichung eine Ampelfarbe zu.

        Die Abweichung wird richtungsabhaengig gebildet und ist niemals
        negativ: Ein Vorsprung gegenueber dem Sollwert ergibt 0.0 und
        damit GRUEN. Die Schwellenwerte sind hier zentral hinterlegt.
        """
        if abweichung >= ROT_AB:
            return Zielstatus.ROT
        if abweichung >= GELB_AB:
            return Zielstatus.GELB
        return Zielstatus.GRUEN
