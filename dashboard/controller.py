"""Steuerung des Ablaufs.

Der Controller holt die Daten ueber das Repository, laesst die Kennzahlen
berechnen und uebergibt sie als Datenobjekte an die Darstellung. Ausserdem
bietet er die Operationen zur Pflege der Daten an.
"""

from datetime import date

from .domaene import (Leistungsstatus, Modul, Notenziel, Studiengang,
                      Terminziel, Zielstatus)
from .dto import (DashboardDatenDTO, FortschrittKachelDTO, LeistungszeileDTO,
                  ModulzeileDTO, NotenKachelDTO, TempoKachelDTO, ZielwertDTO)
from .repository import StudiengangRepository
from .services import FortschrittService, NotenService

LAUFEND = (Leistungsstatus.IN_BEARBEITUNG, Leistungsstatus.EINGEREICHT)


class DashboardController:
    def __init__(self, repository: StudiengangRepository,
                 fortschritt: FortschrittService | None = None,
                 noten: NotenService | None = None) -> None:
        self.repository = repository
        self.fortschritt = fortschritt or FortschrittService()
        self.noten = noten or NotenService()

    # ------------------------------------------------------------ lesen
    def lade_daten(self, stichtag: date | None = None) -> DashboardDatenDTO:
        stichtag = stichtag or date.today()
        sg = self.repository.laden()
        return DashboardDatenDTO(
            stichtag=stichtag,
            studiengang=sg.bezeichnung,
            fortschritt=self._fortschritt(sg, stichtag),
            noten=self._noten(sg, stichtag),
            tempo=self._tempo(sg, stichtag),
            laufende_module=[self._zeile(m) for m in sg.module
                             if m.status in LAUFEND],
            alle_module=[self._zeile(m) for m in sg.module])

    def _terminziel(self, sg: Studiengang) -> Terminziel | None:
        for ziel in sg.ziele:
            if isinstance(ziel, Terminziel):
                return ziel
        return None

    def _fortschritt(self, sg: Studiengang, stichtag: date):
        ziel = self._terminziel(sg)
        soll_zielbild = ziel.soll_ects(sg, stichtag) if ziel else 0.0
        soll_regelende = self.fortschritt.soll_ects(
            sg, sg.regelenddatum, stichtag)
        return FortschrittKachelDTO(
            gesamt_ects=sg.gesamt_ects,
            erreichte_ects=sg.erreichte_ects,
            ects_nach_status=self.fortschritt.ects_nach_status(sg),
            soll_ects_zielbild=soll_zielbild,
            soll_ects_regelende=soll_regelende,
            abweichung_ects=sg.erreichte_ects - soll_zielbild,
            vorsprung_regelende=sg.erreichte_ects - soll_regelende,
            status=ziel.status(sg, stichtag) if ziel else Zielstatus.GRUEN)

    def _noten(self, sg: Studiengang, stichtag: date):
        notenziele = [z for z in sg.ziele if isinstance(z, Notenziel)]
        werte, restschnitte = [], {}
        for ziel in notenziele:
            restschnitte[ziel.bezeichnung] = self.noten.restschnitt(sg, ziel)
            werte.append(ZielwertDTO(
                bezeichnung=ziel.bezeichnung,
                zielwert=ziel.zielnote,
                sollwert=ziel.zielnote,
                abweichung=ziel.abweichung(sg, stichtag),
                status=ziel.status(sg, stichtag)))
        # Massgeblich fuer die Kachel ist das anspruchsvollste Ziel
        status = min((w.status for w in werte),
                     key=lambda s: list(Zielstatus).index(s),
                     default=Zielstatus.GRUEN)
        return NotenKachelDTO(
            durchschnitt=sg.notendurchschnitt,
            bewertete_ects=sg.bewertete_ects,
            benotbare_ects=sg.benotbare_ects,
            korridor=self.noten.korridor(sg),
            ziele=werte, restschnitt_je_ziel=restschnitte, status=status)

    def _tempo(self, sg: Studiengang, stichtag: date):
        ziel = self._terminziel(sg)
        bezug = ziel.zieldatum if ziel else sg.regelenddatum
        return TempoKachelDTO(
            ist_tempo=sg.ist_tempo(stichtag),
            soll_tempo_zielbild=self.fortschritt.soll_tempo(
                sg, bezug, stichtag),
            soll_tempo_regelende=self.fortschritt.soll_tempo(
                sg, sg.regelenddatum, stichtag),
            abweichung=self.fortschritt.tempo_abweichung(sg, bezug, stichtag),
            status=self.fortschritt.tempo_status(sg, bezug, stichtag))

    def _zeile(self, modul: Modul) -> ModulzeileDTO:
        return ModulzeileDTO(
            modulnummer=modul.modulnummer, bezeichnung=modul.bezeichnung,
            ects=modul.ects, status=modul.status, note=modul.note,
            leistungen=[LeistungszeileDTO(
                bezeichnung=l.bezeichnung, ects_anteil=l.ects_anteil,
                form=getattr(l, "form", None), status=l.status,
                note=getattr(l, "note", None), benotbar=l.ist_benotbar())
                for l in modul.leistungen])

    def vorschau_note(self, modulnummer: str, bezeichnung: str,
                      note: float | None,
                      stichtag: date | None = None) -> NotenKachelDTO:
        """Berechnet die Notenkachel, als waere die Note eingetragen.

        Die Aenderung wird nicht gespeichert. Da das Repository bei jedem
        Aufruf neue Objekte erzeugt, bleibt der gespeicherte Stand
        unberuehrt. Der Notendurchschnitt stammt dabei unveraendert aus
        dem Studiengang und wird nicht gesondert berechnet.
        """
        stichtag = stichtag or date.today()
        sg = self.repository.laden()
        leistung = self._finde_leistung(sg, modulnummer, bezeichnung)
        if not hasattr(leistung, "note"):
            raise ValueError("Leistung wird nicht benotet.")
        leistung.note = note
        return self._noten(sg, stichtag)

    def _finde_leistung(self, sg: Studiengang, modulnummer: str,
                        bezeichnung: str):
        for modul in sg.module:
            if modul.modulnummer != modulnummer:
                continue
            for leistung in modul.leistungen:
                if leistung.bezeichnung == bezeichnung:
                    return leistung
        raise KeyError(
            f"Leistung {bezeichnung} in {modulnummer} nicht gefunden.")

    # ---------------------------------------------------------- schreiben
    def setze_note(self, modulnummer: str, bezeichnung: str,
                   note: float | None) -> None:
        """Traegt eine Note ein und setzt den Status auf abgeschlossen."""
        sg = self.repository.laden()
        leistung = self._finde_leistung(sg, modulnummer, bezeichnung)
        if not hasattr(leistung, "note"):
            raise ValueError("Leistung wird nicht benotet.")
        if note is not None and not 1.0 <= note <= 5.0:
            raise ValueError("Note muss zwischen 1,0 und 5,0 liegen.")
        leistung.note = note
        if note is not None:
            leistung.status = Leistungsstatus.ABGESCHLOSSEN
        self.repository.speichern(sg)

    def aendere_status(self, modulnummer: str, bezeichnung: str,
                       status: Leistungsstatus) -> None:
        sg = self.repository.laden()
        self._finde_leistung(sg, modulnummer, bezeichnung).status = status
        self.repository.speichern(sg)

    def lege_modul_an(self, modul: Modul) -> None:
        sg = self.repository.laden()
        if any(m.modulnummer == modul.modulnummer for m in sg.module):
            raise ValueError(f"Modulnummer {modul.modulnummer} existiert bereits.")
        sg.module.append(modul)
        self.repository.speichern(sg)
