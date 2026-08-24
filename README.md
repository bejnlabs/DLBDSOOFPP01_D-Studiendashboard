# Studiendashboard

Dashboard zur Überwachung des eigenen Studienfortschritts. Entstanden als
Portfolioarbeit im Kurs "Objektorientierte und funktionale Programmierung mit
Python" (DLBDSOOFPP01_D) an der IU Internationalen Hochschule.

## Überwachte Ziele

| Ziel | Kennzahl |
|---|---|
| Abschluss bis zum Zieldatum | Studienfortschritt in ECTS gegen den Sollstand |
| Notendurchschnitt | aktueller Schnitt, erforderlicher Restschnitt, erreichbarer Korridor |
| Frühindikator | Arbeitstempo in ECTS pro Monat |

## Installation

Voraussetzung ist Python 3.10 oder neuer. Entwickelt und getestet wurde unter
Python 3.14.5 auf Windows 11 mit der PowerShell.

```powershell
cd DLBDSOOFPP01_D-Studiendashboard
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Der Aufruf über `python.exe` aus der virtuellen Umgebung vermeidet, dass die
Ausführungsrichtlinie von PowerShell angepasst werden muss. Das vorangestellte
kaufmännische Und ist erforderlich, da PowerShell einen mit einem Punkt
beginnenden Pfad sonst als Modulnamen liest.

## Start

Grafische Oberfläche im Browser. Beim ersten Start fragt Streamlit nach einer
E-Mail-Adresse. Die Abfrage lässt sich mit der Eingabetaste überspringen.
Beenden mit Strg + C.

```powershell
& .\.venv\Scripts\python.exe -m streamlit run app_streamlit.py
```

Kommandozeile als Rückfallebene, ohne Zusatzpakete lauffähig.

```powershell
& .\.venv\Scripts\python.exe app_cli.py
```

## Aufbau

```
dashboard/
  domaene/      Fachklassen, Aufzählungstypen, Berechnungsregeln
  repository.py Zugriff auf die Speicherung (Protokoll und JSON-Umsetzung)
  services.py   Vorausberechnungen und Zielvergleiche
  dto.py        Datenobjekte für die Übergabe an die Darstellung
  controller.py Ablaufsteuerung und Pflegeoperationen
  views/        Kommandozeile und Streamlit
  app.py        Erzeugung und Verknüpfung der Objekte
daten/          Studiendaten im JSON-Format
tests/          automatisierte Tests
```

## Daten

Die Studiendaten liegen in `daten/studiengang.json` und lassen sich in einem
Texteditor oder über die grafische Oberfläche pflegen. Der Ausgangsstand wird
über den folgenden Aufruf wiederhergestellt; von Hand vorgenommene Änderungen
werden dabei überschrieben.

```powershell
& .\.venv\Scripts\python.exe erzeuge_daten.py
```

Der Modulkatalog folgt dem Studienablaufplan B.Sc. Angewandte Künstliche
Intelligenz im Modell Teilzeit I. Als Modulnummern dienen die dort
ausgewiesenen Kurscodes, etwa `DLBDSOOFPP01_D` für diesen Kurs. Die Semester 1
und 2 bilden den bisherigen Verlauf ab, die Semester 3 bis 8 die Planung bis
zum Ende der Regelstudienzeit.
