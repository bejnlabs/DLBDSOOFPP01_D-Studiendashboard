"""Automatisierte Tests des Studien-Dashboards.

Ausfuehrung:  python -m unittest discover -s tests
"""

import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dashboard.controller import DashboardController
from dashboard.domaene import (AnerkannteLeistung, Benotet, Leistungsstatus,
                               Modul, Modulart, Notenziel, Pruefungsform,
                               Semester, Studiengang, Studienleistung,
                               Terminziel, Unbenotet, Zielstatus, runde)
from dashboard.repository import JsonStudiengangRepository, StudiengangRepository
from dashboard.services import FortschrittService, NotenService
from dashboard.views import CliView, DashboardView

START, REGELENDE = date(2025, 9, 18), date(2029, 8, 15)
ZIELBILD, STICHTAG = date(2027, 12, 31), date(2026, 8, 10)


def beispiel_studiengang() -> Studiengang:
    module = [
        Modul(modulnummer="ANE01", bezeichnung="Anerkennung", ects=10,
              leistungen=[AnerkannteLeistung(
                  bezeichnung="Anerkennung", ects_anteil=10,
                  status=Leistungsstatus.ABGESCHLOSSEN, herkunft="Vorstudium")]),
        Modul(modulnummer="PRA01", bezeichnung="Praktikum", ects=30,
              art=Modulart.PRAKTIKUM,
              leistungen=[Unbenotet(
                  bezeichnung="Praxisreflexion", ects_anteil=30,
                  status=Leistungsstatus.IN_BEARBEITUNG,
                  form=Pruefungsform.PRAXISREFLEXION, bestanden=False)]),
        Modul(modulnummer="ABS01", bezeichnung="Abschlussmodul", ects=10,
              art=Modulart.ABSCHLUSSMODUL,
              leistungen=[
                  Benotet(bezeichnung="Bachelorarbeit", ects_anteil=9,
                          status=Leistungsstatus.ABGESCHLOSSEN,
                          form=Pruefungsform.BACHELORARBEIT, note=1.7),
                  Benotet(bezeichnung="Kolloquium", ects_anteil=1,
                          status=Leistungsstatus.ABGESCHLOSSEN,
                          form=Pruefungsform.KOLLOQUIUM, note=2.0)]),
    ]
    for i, note in enumerate([1.7, 1.7, 2.7, 2.7, 3.0, 3.0, 3.7, 3.7], start=1):
        module.append(Modul(
            modulnummer=f"KUR{i:02d}", bezeichnung=f"Kursmodul {i}", ects=5,
            leistungen=[Benotet(bezeichnung=f"Kursmodul {i}", ects_anteil=5,
                                status=Leistungsstatus.ABGESCHLOSSEN,
                                form=Pruefungsform.PRUEFUNG, note=note)]))
    rest = 180 - sum(m.ects for m in module)
    module.append(Modul(
        modulnummer="OFF01", bezeichnung="Offene Module", ects=rest,
        leistungen=[Benotet(bezeichnung="Offene Module", ects_anteil=rest,
                            status=Leistungsstatus.OFFEN,
                            form=Pruefungsform.PRUEFUNG, note=None)]))
    return Studiengang(
        bezeichnung="Testgang", gesamt_ects=180, startdatum=START,
        regelenddatum=REGELENDE, module=module,
        semester=[Semester(nummer=1, module=module[3:6])],
        ziele=[Terminziel(bezeichnung="Zielbild", zieldatum=ZIELBILD),
               Notenziel(bezeichnung="Wunschziel", zielnote=2.0),
               Notenziel(bezeichnung="Realistisch", zielnote=2.5)])


class TestLeistungshierarchie(unittest.TestCase):
    def test_oberklasse_ist_abstrakt(self):
        with self.assertRaises(TypeError):
            Studienleistung(bezeichnung="X", ects_anteil=5)

    def test_polymorphes_verhalten(self):
        benotet = Benotet(bezeichnung="B", ects_anteil=5,
                          form=Pruefungsform.PRUEFUNG, note=2.3)
        unbenotet = Unbenotet(bezeichnung="U", ects_anteil=30,
                              form=Pruefungsform.PRAXISREFLEXION, bestanden=True)
        anerkannt = AnerkannteLeistung(bezeichnung="A", ects_anteil=5,
                                       herkunft="Vorstudium")
        self.assertEqual([l.zaehlt_fuer_note() for l in
                          (benotet, unbenotet, anerkannt)], [True, False, False])
        self.assertEqual([l.zaehlt_fuer_tempo() for l in
                          (benotet, unbenotet, anerkannt)], [True, True, False])

    def test_unbewertete_leistung_zaehlt_nicht(self):
        offen = Benotet(bezeichnung="B", ects_anteil=5,
                        form=Pruefungsform.PRUEFUNG, note=None)
        self.assertFalse(offen.ist_bewertet())
        self.assertFalse(offen.zaehlt_fuer_note())
        self.assertFalse(offen.ist_bestanden())


class TestModulnote(unittest.TestCase):
    """Rueckmeldung 4: Ableitungsregel der Modulnote."""

    def setUp(self):
        self.sg = beispiel_studiengang()
        self.abschluss = next(m for m in self.sg.module
                              if m.modulnummer == "ABS01")

    def test_gewichtetes_mittel_mehrerer_leistungen(self):
        # 9 ECTS mit 1,7 und 1 ECTS mit 2,0 ergeben 1,73
        self.assertAlmostEqual(self.abschluss.note, 1.73, places=4)

    def test_ohne_bewertete_leistung_kein_wert(self):
        offen = next(m for m in self.sg.module if m.modulnummer == "OFF01")
        self.assertIsNone(offen.note)

    def test_unbenotetes_modul_hat_keine_note(self):
        praktikum = next(m for m in self.sg.module
                         if m.modulnummer == "PRA01")
        self.assertIsNone(praktikum.note)

    def test_schnitt_wird_nicht_ueber_modulnoten_gebildet(self):
        """Der Studiengangschnitt entsteht direkt aus den Leistungen."""
        paare = [(l.note, l.ects_anteil) for l in self.sg.alle_leistungen
                 if l.zaehlt_fuer_note()]
        erwartet = sum(n * e for n, e in paare) / sum(e for _, e in paare)
        self.assertAlmostEqual(self.sg.notendurchschnitt, erwartet, places=9)


class TestKennzahlen(unittest.TestCase):
    def setUp(self):
        self.sg = beispiel_studiengang()

    def test_erreichte_und_selbst_erbrachte_ects(self):
        self.assertEqual(self.sg.erreichte_ects, 60)          # inkl. 10 anerkannt
        self.assertEqual(self.sg.selbst_erbrachte_ects, 50)   # ohne Anerkennung

    def test_benotbare_ects_ohne_praktikum_und_anerkennung(self):
        self.assertEqual(self.sg.benotbare_ects, 140)

    def test_anerkannte_leistung_erhoeht_tempo_nicht(self):
        ohne = self.sg.ist_tempo(STICHTAG)
        naiv = self.sg.erreichte_ects / ((STICHTAG - START).days / 30.44)
        self.assertLess(ohne, naiv)


class TestAmpellogik(unittest.TestCase):
    """Rueckmeldung 1: richtungsabhaengige Abweichung."""

    def setUp(self):
        self.sg = beispiel_studiengang()
        self.dienst = FortschrittService()

    def test_schwellenwerte(self):
        self.assertEqual(Zielstatus.aus_abweichung(0.09), Zielstatus.GRUEN)
        self.assertEqual(Zielstatus.aus_abweichung(0.10), Zielstatus.GELB)
        self.assertEqual(Zielstatus.aus_abweichung(0.20), Zielstatus.ROT)

    def test_vorsprung_ergibt_gruen(self):
        """Ein Vorsprung darf nicht als Abweichung gewertet werden."""
        ziel = Terminziel(bezeichnung="Fern", zieldatum=date(2035, 1, 1))
        self.assertEqual(ziel.abweichung(self.sg, STICHTAG), 0.0)
        self.assertEqual(ziel.status(self.sg, STICHTAG), Zielstatus.GRUEN)

    def test_rueckstand_ergibt_rot(self):
        ziel = Terminziel(bezeichnung="Nah", zieldatum=date(2026, 12, 31))
        self.assertGreater(ziel.abweichung(self.sg, STICHTAG), 0.20)
        self.assertEqual(ziel.status(self.sg, STICHTAG), Zielstatus.ROT)

    def test_note_besser_als_ziel_ergibt_gruen(self):
        ziel = Notenziel(bezeichnung="Locker", zielnote=4.0)
        self.assertEqual(ziel.abweichung(self.sg), 0.0)
        self.assertEqual(ziel.status(self.sg), Zielstatus.GRUEN)

    def test_note_schlechter_als_ziel_ergibt_abweichung(self):
        ziel = Notenziel(bezeichnung="Streng", zielnote=1.0)
        self.assertGreater(ziel.abweichung(self.sg), 0.20)

    def test_tempo_ueber_soll_ergibt_gruen(self):
        abw = self.dienst.tempo_abweichung(self.sg, date(2040, 1, 1), STICHTAG)
        self.assertEqual(abw, 0.0)


class TestZielnoteAusZielobjekt(unittest.TestCase):
    """Rueckmeldung 2: Zielnote stammt aus dem Zielobjekt."""

    def test_restschnitt_nutzt_zielnote_des_objekts(self):
        sg = beispiel_studiengang()
        dienst = NotenService()
        werte = {z.zielnote: dienst.restschnitt(sg, z)
                 for z in sg.ziele if isinstance(z, Notenziel)}
        self.assertEqual(len(werte), 2)
        # Ein strengeres Ziel verlangt einen besseren Restschnitt
        self.assertLess(werte[2.0], werte[2.5])

    def test_beliebige_zielnote_wird_uebernommen(self):
        sg = beispiel_studiengang()
        ziel = Notenziel(bezeichnung="Frei", zielnote=1.8)
        erwartet = ((1.8 * sg.benotbare_ects
                     - sg.notendurchschnitt * sg.bewertete_ects)
                    / (sg.benotbare_ects - sg.bewertete_ects))
        self.assertAlmostEqual(NotenService().restschnitt(sg, ziel),
                               erwartet, places=9)


class TestEindeutigeZustaendigkeit(unittest.TestCase):
    """Rueckmeldung 3: nur eine Quelle fuer den Notendurchschnitt."""

    def test_notenservice_berechnet_keinen_durchschnitt(self):
        self.assertFalse(hasattr(NotenService(), "durchschnitt"))

    def test_durchschnitt_liegt_am_studiengang(self):
        sg = beispiel_studiengang()
        self.assertIsNotNone(sg.notendurchschnitt)

    def test_durchschnitt_ist_schreibgeschuetzt(self):
        sg = beispiel_studiengang()
        with self.assertRaises(AttributeError):
            sg.notendurchschnitt = 1.0


class TestBeziehungen(unittest.TestCase):
    def test_aggregation_modul_bleibt_erhalten(self):
        sg = beispiel_studiengang()
        semester = sg.semester[0]
        modul = semester.module[0]
        semester.entferne(modul)
        self.assertNotIn(modul, semester.module)
        self.assertIn(modul, sg.module)


class TestProtokolle(unittest.TestCase):
    def test_cliview_erfuellt_protokoll(self):
        self.assertIsInstance(CliView(), DashboardView)

    def test_json_repository_erfuellt_protokoll(self):
        self.assertIsInstance(JsonStudiengangRepository("x.json"),
                              StudiengangRepository)


class TestRepository(unittest.TestCase):
    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory()
        self.pfad = Path(self.ordner.name) / "sg.json"
        self.repo = JsonStudiengangRepository(self.pfad)

    def tearDown(self):
        self.ordner.cleanup()

    def test_speichern_und_laden(self):
        original = beispiel_studiengang()
        self.repo.speichern(original)
        geladen = self.repo.laden()
        self.assertEqual(geladen.erreichte_ects, original.erreichte_ects)
        self.assertAlmostEqual(geladen.notendurchschnitt,
                               original.notendurchschnitt, places=9)
        self.assertEqual(len(geladen.module), len(original.module))
        self.assertEqual(len(geladen.ziele), len(original.ziele))

    def test_enum_wird_als_text_gespeichert(self):
        self.repo.speichern(beispiel_studiengang())
        inhalt = self.pfad.read_text(encoding="utf-8")
        self.assertIn('"abgeschlossen"', inhalt)


class TestController(unittest.TestCase):
    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory()
        pfad = Path(self.ordner.name) / "sg.json"
        JsonStudiengangRepository(pfad).speichern(beispiel_studiengang())
        self.controller = DashboardController(JsonStudiengangRepository(pfad))

    def tearDown(self):
        self.ordner.cleanup()

    def test_lade_daten_liefert_alle_kacheln(self):
        daten = self.controller.lade_daten(STICHTAG)
        self.assertEqual(daten.fortschritt.gesamt_ects, 180)
        self.assertEqual(len(daten.noten.ziele), 2)
        self.assertGreater(daten.tempo.soll_tempo_zielbild, 0)
        self.assertTrue(daten.alle_module)

    def test_note_eintragen_wird_gespeichert(self):
        self.controller.setze_note("OFF01", "Offene Module", 2.0)
        daten = self.controller.lade_daten(STICHTAG)
        zeile = next(m for m in daten.alle_module if m.modulnummer == "OFF01")
        self.assertAlmostEqual(zeile.note, 2.0)
        self.assertEqual(zeile.status, Leistungsstatus.ABGESCHLOSSEN)

    def test_ungueltige_note_wird_abgelehnt(self):
        with self.assertRaises(ValueError):
            self.controller.setze_note("OFF01", "Offene Module", 7.0)

    def test_unbekannte_leistung_meldet_fehler(self):
        with self.assertRaises(KeyError):
            self.controller.setze_note("XXX", "Gibt es nicht", 2.0)


class TestRundung(unittest.TestCase):
    def test_kaufmaennische_rundung(self):
        self.assertEqual(runde(2.775), 2.78)
        self.assertIsNone(runde(None))


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestStreamlitAnsicht(unittest.TestCase):
    """Durchlauf der grafischen Ansicht mit einer Streamlit-Attrappe.

    Ersetzt keinen Test im Browser, deckt aber Namens- und Zugriffsfehler
    in der Ansicht auf.
    """

    def setUp(self):
        import streamlit_attrappe
        streamlit_attrappe.installieren()
        streamlit_attrappe.aufrufe.clear()
        self.attrappe = streamlit_attrappe
        self.ordner = tempfile.TemporaryDirectory()
        self.pfad = Path(self.ordner.name) / "sg.json"
        JsonStudiengangRepository(self.pfad).speichern(beispiel_studiengang())
        self.controller = DashboardController(JsonStudiengangRepository(self.pfad))

    def tearDown(self):
        self.ordner.cleanup()
        sys.modules.pop("streamlit", None)

    def test_ansicht_laeuft_vollstaendig_durch(self):
        from dashboard.views.streamlit_view import StreamlitView
        view = StreamlitView(controller=self.controller)
        view.zeige(self.controller.lade_daten(STICHTAG))
        for erwartet in ("title", "progress", "spalte.metric", "selectbox",
                         "form_submit_button", "dataframe"):
            self.assertIn(erwartet, self.attrappe.aufrufe,
                          f"{erwartet} wurde nicht aufgerufen")

    def test_ansicht_erfuellt_protokoll(self):
        from dashboard.views.streamlit_view import StreamlitView
        self.assertIsInstance(StreamlitView(), DashboardView)


class TestVorschau(unittest.TestCase):
    """Die Vorschau darf den gespeicherten Stand nicht veraendern."""

    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory()
        self.pfad = Path(self.ordner.name) / "sg.json"
        JsonStudiengangRepository(self.pfad).speichern(beispiel_studiengang())
        self.controller = DashboardController(JsonStudiengangRepository(self.pfad))

    def tearDown(self):
        self.ordner.cleanup()

    def test_vorschau_speichert_nicht(self):
        vorher = self.pfad.read_text(encoding="utf-8")
        self.controller.vorschau_note("OFF01", "Offene Module", 1.0, STICHTAG)
        self.assertEqual(self.pfad.read_text(encoding="utf-8"), vorher)

    def test_vorschau_zeigt_wirkung(self):
        alt = self.controller.lade_daten(STICHTAG).noten
        neu = self.controller.vorschau_note("OFF01", "Offene Module", 1.0,
                                            STICHTAG)
        self.assertLess(neu.durchschnitt, alt.durchschnitt)
        self.assertGreater(neu.bewertete_ects, alt.bewertete_ects)

    def test_vorschau_nutzt_domaenenberechnung(self):
        """Der Durchschnitt stammt aus dem Studiengang, nicht aus dem Dienst."""
        neu = self.controller.vorschau_note("OFF01", "Offene Module", 2.0,
                                            STICHTAG)
        sg = JsonStudiengangRepository(self.pfad).laden()
        leistung = next(l for m in sg.module for l in m.leistungen
                        if m.modulnummer == "OFF01")
        leistung.note = 2.0
        self.assertAlmostEqual(neu.durchschnitt, sg.notendurchschnitt,
                               places=9)

    def test_vorschau_meldet_unbekannte_leistung(self):
        with self.assertRaises(KeyError):
            self.controller.vorschau_note("XXX", "Gibt es nicht", 2.0)


class TestLeistungszeilen(unittest.TestCase):
    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory()
        pfad = Path(self.ordner.name) / "sg.json"
        JsonStudiengangRepository(pfad).speichern(beispiel_studiengang())
        self.daten = DashboardController(
            JsonStudiengangRepository(pfad)).lade_daten(STICHTAG)

    def tearDown(self):
        self.ordner.cleanup()

    def test_abschlussmodul_hat_zwei_leistungen(self):
        modul = next(m for m in self.daten.alle_module
                     if m.modulnummer == "ABS01")
        self.assertEqual(len(modul.leistungen), 2)
        self.assertEqual({l.ects_anteil for l in modul.leistungen}, {9, 1})

    def test_praktikum_ist_nicht_benotbar(self):
        modul = next(m for m in self.daten.alle_module
                     if m.modulnummer == "PRA01")
        self.assertFalse(any(l.benotbar for l in modul.leistungen))

    def test_anerkannte_leistung_ohne_pruefungsform(self):
        modul = next(m for m in self.daten.alle_module
                     if m.modulnummer == "ANE01")
        self.assertIsNone(modul.leistungen[0].form)
