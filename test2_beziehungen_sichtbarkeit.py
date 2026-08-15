"""
Testprogramm 2 - Beziehungen und Sichtbarkeit
Gehoert zum ersten Teil von Abschnitt 1.2 des Reflexionsdokuments.

Untersucht wird, ob Python eigene Sprachmittel fuer Komposition und
Aggregation kennt und ob sich die Sichtbarkeitsangaben des
Klassendiagramms durchsetzen lassen.
"""


class Modul:
    def __init__(self, bezeichnung: str, ects: int) -> None:
        self.bezeichnung = bezeichnung
        self.ects = ects

    def __repr__(self) -> str:
        return f"Modul({self.bezeichnung})"


class Semester:
    """Aggregation: haelt nur Verweise auf bestehende Module."""

    def __init__(self, nummer: int) -> None:
        self.nummer = nummer
        self.module: list[Modul] = []

    def ordne_zu(self, modul: Modul) -> None:
        self.module.append(modul)

    def entferne(self, modul: Modul) -> None:
        """Loest die Zuordnung. Das Modul selbst bleibt bestehen."""
        self.module.remove(modul)


class Studiengang:
    """Komposition: erzeugt seine Semester selbst und gibt sie auf."""

    def __init__(self, bezeichnung: str) -> None:
        self.bezeichnung = bezeichnung
        self.semester: list[Semester] = []
        self._puffer = 0.1  # geschuetzt, nur Konvention
        self.__intern = "gesperrt"  # privat, Name Mangling

    def erzeuge_semester(self, nummer: int) -> Semester:
        neues = Semester(nummer)
        self.semester.append(neues)
        return neues

    def loesche(self) -> None:
        """Beendet die Lebensdauer der Teile mit."""
        self.semester.clear()


print("a) Komposition und Aggregation im Quelltext")
katalog = [Modul("Mathematik Grundlagen", 5), Modul("Cloud Programming", 5)]
sg = Studiengang("Angewandte Kuenstliche Intelligenz")
sem1 = sg.erzeuge_semester(1)
for m in katalog:
    sem1.ordne_zu(m)

print(f"   Katalog:    {katalog}")
print(f"   Semester 1: {sem1.module}")
print("   Beide Beziehungen sind im Quelltext identisch: eine Liste von Verweisen.")

sem1.entferne(katalog[0])
print(f"\n   nach entferne() - Semester: {sem1.module}")
print(f"   nach entferne() - Katalog:  {katalog}   <- Modul existiert weiter")

sg.loesche()
print(f"   nach loesche()  - Semester des Studiengangs: {sg.semester}")
print("   Der Unterschied entsteht durch das Verhalten der Methoden,")
print("   nicht durch ein Sprachmittel.")

print("\nb) Sichtbarkeit")
print(f"   oeffentlich (+): {sg.bezeichnung}")
print(f"   geschuetzt (#):  {sg._puffer}   <- Zugriff funktioniert trotzdem")
try:
    print(sg.__intern)
except AttributeError as fehler:
    print(f"   privat (-):      AttributeError: {fehler}")
print(f"   Umgehung:        {sg._Studiengang__intern}")
print("   Python kennt keine echte Kapselung, nur Konventionen.")
