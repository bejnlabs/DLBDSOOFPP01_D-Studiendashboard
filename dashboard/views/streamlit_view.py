"""Grafische Darstellung mit Streamlit.

Die Ansicht enthaelt keine Fachlogik. Saemtliche Werte stammen aus dem
uebergebenen Datenobjekt. Fuer die Pflege der Daten greift sie auf die
Kommandooperationen des Controllers zurueck.
"""

import streamlit as st

from ..domaene import Leistungsstatus, Zielstatus, runde
from ..dto import DashboardDatenDTO

FARBE = {
    Zielstatus.GRUEN: "#1D9E75",
    Zielstatus.GELB: "#EF9F27",
    Zielstatus.ROT: "#E24B4A",
}
BESCHRIFTUNG = {
    Zielstatus.GRUEN: "im Plan",
    Zielstatus.GELB: "eng",
    Zielstatus.ROT: "kritisch",
}
NOTEN = [1.0, 1.3, 1.7, 2.0, 2.3, 2.7, 3.0, 3.3, 3.7, 4.0, 5.0]
STATUSFARBE = {
    Leistungsstatus.ABGESCHLOSSEN: "#1D9E75",
    Leistungsstatus.EINGEREICHT: "#378ADD",
    Leistungsstatus.IN_BEARBEITUNG: "#EF9F27",
    Leistungsstatus.OFFEN: "#D3D1C7",
}


class StreamlitView:
    def __init__(self, controller=None) -> None:
        self.controller = controller

    def zeige(self, daten: DashboardDatenDTO) -> None:
        st.set_page_config(page_title="Studiendashboard", layout="centered")
        st.title("Studien-Dashboard")
        st.caption(f"{daten.studiengang} · Stand {daten.stichtag.strftime('%d.%m.%Y')}")
        self._fortschritt(daten)
        st.divider()
        self._noten(daten)
        st.divider()
        self._tempo(daten)
        st.divider()
        self._module(daten)
        if self.controller is not None:
            st.divider()
            self._pflege(daten)

    def _ampel(self, status: Zielstatus) -> str:
        return (
            f"<span style='background:{FARBE[status]};color:white;"
            f"padding:2px 10px;border-radius:10px;font-size:0.8rem'>"
            f"{BESCHRIFTUNG[status]}</span>"
        )

    def _ueberschrift(self, text: str, status: Zielstatus) -> None:
        st.markdown(f"### {text} &nbsp; {self._ampel(status)}", unsafe_allow_html=True)

    def _fortschritt(self, daten: DashboardDatenDTO) -> None:
        f = daten.fortschritt
        self._ueberschrift("Ziel 1: Studienfortschritt", f.status)
        anteil = f.erreichte_ects / f.gesamt_ects if f.gesamt_ects else 0.0
        st.progress(min(1.0, anteil))
        st.write(f"**{f.erreichte_ects:.0f} von {f.gesamt_ects} ECTS** ({anteil:.1%})")

        segmente = "".join(
            f"<div style='width:{f.ects_nach_status.get(s, 0) / f.gesamt_ects:.4%};"
            f"background:{STATUSFARBE[s]};height:22px'></div>"
            for s in Leistungsstatus
        )
        st.markdown(
            f"<div style='display:flex;border-radius:4px;"
            f"overflow:hidden'>{segmente}</div>",
            unsafe_allow_html=True,
        )
        legende = " &nbsp; ".join(
            f"<span style='color:{STATUSFARBE[s]}'>&#9632;</span> "
            f"{s.value} {f.ects_nach_status.get(s, 0):.0f}"
            for s in Leistungsstatus
            if f.ects_nach_status.get(s, 0)
        )
        st.markdown(
            f"<div style='font-size:0.78rem;margin-top:6px'>{legende}</div>",
            unsafe_allow_html=True,
        )

        s1, s2 = st.columns(2)
        s1.metric(
            "Soll Zielbild",
            f"{f.soll_ects_zielbild:.1f} ECTS",
            f"{f.abweichung_ects:+.1f}",
        )
        s2.metric(
            "Soll Regelende",
            f"{f.soll_ects_regelende:.1f} ECTS",
            f"{f.vorsprung_regelende:+.1f}",
        )

    def _noten(self, daten: DashboardDatenDTO) -> None:
        n = daten.noten
        self._ueberschrift("Ziel 2: Notendurchschnitt", n.status)
        if n.durchschnitt is None:
            st.info("Noch keine bewertete Leistung vorhanden.")
            return
        s1, s2 = st.columns(2)
        s1.metric("Aktueller Schnitt", f"{runde(n.durchschnitt):.2f}")
        s2.metric("Bewertete ECTS", f"{n.bewertete_ects:.0f} / {n.benotbare_ects:.0f}")
        if n.korridor:
            st.caption(
                f"Erreichbarer Korridor {runde(n.korridor[0]):.2f} bis "
                f"{runde(n.korridor[1]):.2f}"
            )
        for ziel in n.ziele:
            rest = n.restschnitt_je_ziel.get(ziel.bezeichnung)
            text = "nicht mehr veraenderbar" if rest is None else f"{runde(rest):.2f}"
            st.markdown(
                f"{ziel.bezeichnung} (Ziel {ziel.zielwert:.1f}): "
                f"Nötiger Restschnitt **{text}** &nbsp; "
                f"{self._ampel(ziel.status)}",
                unsafe_allow_html=True,
            )

    def _tempo(self, daten: DashboardDatenDTO) -> None:
        t = daten.tempo
        self._ueberschrift("Frühindikator: Arbeitstempo", t.status)
        s1, s2, s3 = st.columns(3)
        s1.metric("Ist", f"{t.ist_tempo:.2f}", help="ECTS pro Monat")
        s2.metric("nötig bis Zielbild", f"{t.soll_tempo_zielbild:.2f}")
        s3.metric("nötig bis Regelende", f"{t.soll_tempo_regelende:.2f}")

    def _module(self, daten: DashboardDatenDTO) -> None:
        st.subheader("Module")
        nur_laufend = st.checkbox("Nur laufende Module", value=True)
        zeilen = daten.laufende_module if nur_laufend else daten.alle_module
        st.dataframe(
            [
                {
                    "Nummer": m.modulnummer,
                    "Modul": m.bezeichnung,
                    "ECTS": m.ects,
                    "Status": m.status.value,
                    "Note": "-" if m.note is None else f"{m.note:.2f}",
                }
                for m in zeilen
            ],
            use_container_width=True,
            hide_index=True,
        )

    def _pflege(self, daten: DashboardDatenDTO) -> None:
        """Maske zur Pflege der Noten.

        Modul und Leistung werden ausgewaehlt statt eingegeben, die
        Notenliste enthaelt nur zulaessige Werte. Vor dem Speichern zeigt
        eine Vorschau, wie sich die Kennzahlen veraendern wuerden.
        """
        st.subheader("Note eintragen")

        module = {
            f"{m.modulnummer} · {m.bezeichnung}": m
            for m in daten.alle_module
            if any(l.benotbar for l in m.leistungen)
        }
        if not module:
            st.info("Keine benotbare Leistung vorhanden.")
            return
        modul = module[st.selectbox("Modul", list(module))]

        leistungen = {self._leistungstext(l): l for l in modul.leistungen if l.benotbar}
        leistung = leistungen[st.selectbox("Leistung", list(leistungen))]

        vorgabe = NOTEN.index(leistung.note) if leistung.note in NOTEN else 3
        with st.form("note_eintragen"):
            note = st.selectbox(
                "Note",
                NOTEN,
                index=vorgabe,
                format_func=lambda n: f"{n:.1f}".replace(".", ","),
            )
            gespeichert = st.form_submit_button("Speichern")

        self._vorschau(daten, modul, leistung, note)

        if gespeichert:
            try:
                self.controller.setze_note(
                    modul.modulnummer, leistung.bezeichnung, note
                )
                st.success(
                    f"{leistung.bezeichnung}: {note:.1f}".replace(".", ",")
                    + " gespeichert."
                )
                st.rerun()
            except (KeyError, ValueError) as fehler:
                st.error(str(fehler))

    def _leistungstext(self, leistung) -> str:
        form = leistung.form.value if leistung.form else "ohne Pruefung"
        return f"{leistung.bezeichnung} · {leistung.ects_anteil:.0f} ECTS · {form}"

    def _vorschau(self, daten: DashboardDatenDTO, modul, leistung, note: float) -> None:
        """Stellt die Wirkung der Note dar, ohne sie zu speichern."""
        try:
            neu = self.controller.vorschau_note(
                modul.modulnummer, leistung.bezeichnung, note, daten.stichtag
            )
        except (KeyError, ValueError) as fehler:
            st.warning(str(fehler))
            return

        alt = daten.noten
        if alt.durchschnitt is None or neu.durchschnitt is None:
            return

        s1, s2, s3 = st.columns(3)
        s1.metric("Schnitt bisher", f"{runde(alt.durchschnitt):.2f}")
        # Bei Noten ist ein kleinerer Wert besser, daher inverse Faerbung
        s2.metric(
            "Schnitt danach",
            f"{runde(neu.durchschnitt):.2f}",
            delta=f"{neu.durchschnitt - alt.durchschnitt:+.2f}",
            delta_color="inverse",
        )
        s3.metric(
            "Bewertete ECTS",
            f"{neu.bewertete_ects:.0f} / {neu.benotbare_ects:.0f}",
            delta=f"{neu.bewertete_ects - alt.bewertete_ects:+.0f}",
        )

        for ziel in neu.ziele:
            vorher = alt.restschnitt_je_ziel.get(ziel.bezeichnung)
            nachher = neu.restschnitt_je_ziel.get(ziel.bezeichnung)
            if vorher is None or nachher is None:
                continue
            st.caption(
                f"Nötiger Restschnitt für Ziel "
                f"{ziel.zielwert:.1f}: {runde(vorher):.2f} → "
                f"**{runde(nachher):.2f}**"
            )
        if neu.korridor:
            st.caption(
                f"Erreichbarer Korridor danach "
                f"{runde(neu.korridor[0]):.2f} bis "
                f"{runde(neu.korridor[1]):.2f}"
            )
