"""Zugriff auf die gespeicherten Studiendaten.

Das Protokoll beschreibt, welche Operationen eine Speicherung anbieten
muss. Die Umsetzung fuer das JSON-Format ist austauschbar, ohne dass die
uebrigen Schichten angepasst werden muessen.
"""

import json
from datetime import date
from pathlib import Path
from typing import Protocol, runtime_checkable

from .domaene import (AnerkannteLeistung, Benotet, Leistungsstatus, Modul,
                      Modulart, Notenziel, Pruefungsform, Semester,
                      Studiengang, Studienleistung, Terminziel, Unbenotet)


@runtime_checkable
class StudiengangRepository(Protocol):
    """Vertrag fuer den Zugriff auf die Studiendaten."""

    def laden(self) -> Studiengang: ...

    def speichern(self, studiengang: Studiengang) -> None: ...


def _datum(wert: str | None) -> date | None:
    return date.fromisoformat(wert) if wert else None


def _text(wert: date | None) -> str | None:
    return wert.isoformat() if wert else None


class JsonStudiengangRepository:
    """Speichert den Studiengang in einer JSON-Datei."""

    def __init__(self, pfad: Path | str) -> None:
        self.pfad = Path(pfad)

    # ------------------------------------------------------------ laden
    def laden(self) -> Studiengang:
        with self.pfad.open("r", encoding="utf-8") as datei:
            roh = json.load(datei)

        module = [self._modul_lesen(m) for m in roh.get("module", [])]
        nach_nummer = {m.modulnummer: m for m in module}

        semester = []
        for s in roh.get("semester", []):
            sem = Semester(nummer=s["nummer"],
                           startdatum=_datum(s.get("startdatum")))
            for nummer in s.get("module", []):
                if nummer in nach_nummer:
                    sem.ordne_zu(nach_nummer[nummer])
            semester.append(sem)

        ziele = [self._ziel_lesen(z) for z in roh.get("ziele", [])]

        return Studiengang(
            bezeichnung=roh["bezeichnung"],
            gesamt_ects=roh["gesamt_ects"],
            startdatum=date.fromisoformat(roh["startdatum"]),
            regelenddatum=date.fromisoformat(roh["regelenddatum"]),
            module=module, semester=semester, ziele=ziele)

    def _modul_lesen(self, roh: dict) -> Modul:
        return Modul(
            modulnummer=roh["modulnummer"],
            bezeichnung=roh["bezeichnung"],
            ects=roh["ects"],
            art=Modulart(roh.get("art", Modulart.KURSMODUL.value)),
            leistungen=[self._leistung_lesen(l)
                        for l in roh.get("leistungen", [])])

    def _leistung_lesen(self, roh: dict) -> Studienleistung:
        typ = roh["typ"]
        gemeinsam = {
            "bezeichnung": roh["bezeichnung"],
            "ects_anteil": roh["ects_anteil"],
            "status": Leistungsstatus(roh.get("status",
                                              Leistungsstatus.OFFEN.value)),
        }
        if typ == "anerkannt":
            return AnerkannteLeistung(
                **gemeinsam, herkunft=roh.get("herkunft", ""),
                anerkennungsdatum=_datum(roh.get("anerkennungsdatum")))

        pruefung = {
            "form": Pruefungsform(roh["form"]),
            "versuch": roh.get("versuch", 1),
            "pruefungsdatum": _datum(roh.get("pruefungsdatum")),
        }
        if typ == "unbenotet":
            return Unbenotet(**gemeinsam, **pruefung,
                             bestanden=roh.get("bestanden", False))
        return Benotet(**gemeinsam, **pruefung, note=roh.get("note"))

    def _ziel_lesen(self, roh: dict):
        if roh["typ"] == "termin":
            return Terminziel(bezeichnung=roh["bezeichnung"],
                              zieldatum=date.fromisoformat(roh["zieldatum"]))
        return Notenziel(bezeichnung=roh["bezeichnung"],
                         zielnote=roh["zielnote"])

    # -------------------------------------------------------- speichern
    def speichern(self, studiengang: Studiengang) -> None:
        roh = {
            "bezeichnung": studiengang.bezeichnung,
            "gesamt_ects": studiengang.gesamt_ects,
            "startdatum": studiengang.startdatum.isoformat(),
            "regelenddatum": studiengang.regelenddatum.isoformat(),
            "ziele": [self._ziel_schreiben(z) for z in studiengang.ziele],
            "module": [self._modul_schreiben(m) for m in studiengang.module],
            "semester": [{"nummer": s.nummer,
                          "startdatum": _text(s.startdatum),
                          "module": [m.modulnummer for m in s.module]}
                         for s in studiengang.semester],
        }
        self.pfad.parent.mkdir(parents=True, exist_ok=True)
        with self.pfad.open("w", encoding="utf-8") as datei:
            json.dump(roh, datei, indent=2, ensure_ascii=False)

    def _modul_schreiben(self, modul: Modul) -> dict:
        return {
            "modulnummer": modul.modulnummer,
            "bezeichnung": modul.bezeichnung,
            "ects": modul.ects,
            "art": modul.art.value,
            "leistungen": [self._leistung_schreiben(l)
                           for l in modul.leistungen],
        }

    def _leistung_schreiben(self, leistung: Studienleistung) -> dict:
        roh = {
            "bezeichnung": leistung.bezeichnung,
            "ects_anteil": leistung.ects_anteil,
            "status": leistung.status.value,
        }
        if isinstance(leistung, AnerkannteLeistung):
            roh.update(typ="anerkannt", herkunft=leistung.herkunft,
                       anerkennungsdatum=_text(leistung.anerkennungsdatum))
            return roh
        roh.update(form=leistung.form.value, versuch=leistung.versuch,
                   pruefungsdatum=_text(leistung.pruefungsdatum))
        if isinstance(leistung, Unbenotet):
            roh.update(typ="unbenotet", bestanden=leistung.bestanden)
        else:
            roh.update(typ="benotet", note=leistung.note)
        return roh

    def _ziel_schreiben(self, ziel) -> dict:
        if isinstance(ziel, Terminziel):
            return {"typ": "termin", "bezeichnung": ziel.bezeichnung,
                    "zieldatum": ziel.zieldatum.isoformat()}
        return {"typ": "note", "bezeichnung": ziel.bezeichnung,
                "zielnote": ziel.zielnote}
