# Studien-Dashboard

Dashboard zur Ueberwachung des eigenen Studienfortschritts. Entstanden als
Portfolioarbeit im Kurs "Objektorientierte und funktionale Programmierung
mit Python" (DLBDSOOFPP01_D) an der IU Internationalen Hochschule.

## Ueberwachte Ziele

| Ziel | Kennzahl |
|---|---|
| Abschluss bis zum Zieldatum | Studienfortschritt in ECTS gegen den Sollstand |
| Notendurchschnitt | aktueller Schnitt, erforderlicher Restschnitt, erreichbarer Korridor |
| Fruehindikator | Arbeitstempo in ECTS pro Monat |

## Installation

Voraussetzung ist Python 3.10 oder neuer. Entwickelt und getestet wurde
unter Python 3.14.5 auf Windows 11.

```powershell
cd studien-dashboard
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Der Aufruf ueber `.venv\Scripts\python.exe` vermeidet, dass die
Ausfuehrungsrichtlinie von PowerShell angepasst werden muss.

## Start

Grafische Oberflaeche im Browser:

```powershell
.venv\Scripts\python.exe -m streamlit run app_streamlit.py
```

Kommandozeile als Rueckfallebene, ohne Zusatzpakete lauffaehig:

```powershell
.venv\Scripts\python.exe app_cli.py
```

Optional laesst sich ein abweichender Stichtag angeben:

```powershell
.venv\Scripts\python.exe app_cli.py 2026-08-10
```

## Tests

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests
```

## Aufbau

```
dashboard/
  domaene/      Fachklassen, Aufzaehlungstypen, Berechnungsregeln
  repository.py Zugriff auf die Speicherung (Protokoll und JSON-Umsetzung)
  services.py   Vorausberechnungen und Zielvergleiche
  dto.py        Datenobjekte fuer die Uebergabe an die Darstellung
  controller.py Ablaufsteuerung und Pflegeoperationen
  views/        Kommandozeile und Streamlit
  app.py        Erzeugung und Verknuepfung der Objekte
daten/          Studiendaten im JSON-Format
tests/          automatisierte Tests
```

## Daten

Die Studiendaten liegen in `daten/studiengang.json` und lassen sich in
einem Texteditor oder ueber die grafische Oberflaeche pflegen. Mit
`python erzeuge_daten.py` wird die Ausgangsdatei neu erzeugt.

Der Modulkatalog folgt dem Studienablaufplan B.Sc. Angewandte
Kuenstliche Intelligenz im Modell Teilzeit I. Als Modulnummern dienen
die dort ausgewiesenen Kurscodes, etwa `DLBDSOOFPP01_D` fuer diesen
Kurs. Module, die noch nicht begonnen wurden, sind keinem Semester
zugeordnet.
