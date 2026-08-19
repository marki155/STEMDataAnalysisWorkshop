# STEM Data Analysis Workshop

EELS- und EDX-Auswertung von STEM-Spektrenbildern mit [HyperSpy](https://hyperspy.org)
und [eXSpy](https://hyperspy.org/exspy/).

Diese Anleitung setzt **keine Python-Kenntnisse** voraus. Wenn du sie von oben nach
unten abarbeitest, hast du in etwa 10 Minuten eine lauffaehige Umgebung -
unter Windows, macOS und Linux gleichermassen.

---

## Was du installierst (und was nicht)

Du installierst **ein einziges Programm**: `pixi`. Alles andere - Python selbst,
HyperSpy, alle Bibliotheken - holt pixi anschliessend automatisch in *exakt* den
Versionen, die in `pixi.lock` festgeschrieben sind.

Das bedeutet:

- **Du brauchst kein Python vorinstalliert.** Auch kein Anaconda, kein Miniconda.
- **Es wird nichts an deinem System veraendert.** Alles landet im Projektordner
  unter `.pixi/`. Zum Deinstallieren reicht es, den Ordner zu loeschen.
- **Alle Teilnehmenden haben dieselben Versionen.** Kein "bei mir laeuft's aber".

---

## Schritt 1: pixi installieren

Such dir dein Betriebssystem heraus und fuehre **einen** Befehl aus.

### Windows

PowerShell oeffnen (Startmenue -> "PowerShell" tippen -> Enter) und eingeben:

```powershell
powershell -ExecutionPolicy ByPass -c "irm -useb https://pixi.sh/install.ps1 | iex"
```

**Danach PowerShell schliessen und neu oeffnen** - sonst kennt Windows den Befehl `pixi` noch nicht.

### macOS

Terminal oeffnen (Cmd+Leertaste -> "Terminal" -> Enter) und eingeben:

```bash
curl -fsSL https://pixi.sh/install.sh | sh
```

**Danach Terminal schliessen und neu oeffnen.**

### Linux

```bash
curl -fsSL https://pixi.sh/install.sh | sh
```

**Danach Terminal schliessen und neu oeffnen.**

### Hat es geklappt?

```bash
pixi --version
```

Wenn eine Versionsnummer erscheint: weiter mit Schritt 2.
Wenn "Befehl nicht gefunden" erscheint: Terminal wirklich neu geoeffnet? Falls ja,
siehe [Wenn etwas nicht funktioniert](#wenn-etwas-nicht-funktioniert).

---

## Schritt 2: Projekt herunterladen

**Mit Git** (empfohlen, weil du spaeter Korrekturen mit `git pull` nachziehen kannst):

```bash
git clone <REPO-URL>
cd STEMDataAnalysisWorkshop
```

**Ohne Git:** Auf der GitHub-Seite auf den gruenen Knopf **Code** klicken ->
**Download ZIP** -> entpacken -> im Terminal in den entpackten Ordner wechseln.

---

## Schritt 3: Messdaten herunterladen

Die Messdaten liegen **nicht** im Repository. Du laedst sie einmalig separat
herunter - das ZIP ist 43 MB gross.

1. Daten-ZIP herunterladen (43 MB, entpackt 152 MB): **<HIER DEN DOWNLOAD-LINK EINTRAGEN>**
2. Entpacken.
3. Den Ordner `nanopore` so ablegen, dass es am Ende **genau so** aussieht:

```
STEMDataAnalysisWorkshop/
├── data/
│   └── nanopore/
│       ├── EELS Spectrum Image (high-loss).dm4
│       ├── EELS Spectrum Image (low-loss).dm4
│       ├── EDS Spectrum Image.dm4
│       ├── ADF Image.dm4
│       ├── ADF Image (SI Survey).dm4
│       └── Si Standards/
├── notebooks/
├── pixi.toml
└── README.md
```

> Notebook 03 braucht einen zweiten Datensatz (`data/praktikum/`), der **nicht**
> im ZIP ist. `pixi run check` meldet ihn als "optional, fehlt" - das ist so
> gewollt und kein Fehler.

> **Der haeufigste Fehler ist ein Ordner zu viel** - also `data/messdaten/nanopore/...`
> statt `data/nanopore/...`. Die Notebooks finden die Dateien meistens auch dann noch,
> aber Schritt 4 sagt dir sicherheitshalber genau, was es wo gefunden hat.

---

## Schritt 4: Umgebung einrichten und pruefen

Im Projektordner:

```bash
pixi run check
```

Beim **ersten** Aufruf laedt pixi Python und alle Bibliotheken herunter - das dauert
je nach Internetverbindung ein paar Minuten und braucht rund 2 GB Platz. Danach geht
es sofort.

Der Befehl prueft der Reihe nach:

1. sind alle Pakete da (mit Versionsnummern),
2. koennen `.dm3`/`.dm4`-Dateien gelesen werden,
3. kennt HyperSpy die EELS- und EDX-Signaltypen,
4. ist die GOSH-Datenbank da (42 MB, wird einmalig geladen - **mach das vor dem
   Workshop**, nicht wenn zwanzig Leute gleichzeitig im WLAN haengen),
5. liegen alle Messdaten am richtigen Ort.

Am Ende steht entweder `Alles bereit.` oder eine Liste dessen, was noch fehlt.

---

## Schritt 5: Loslegen

```bash
pixi run lab
```

JupyterLab oeffnet sich im Browser. Arbeite die Notebooks in dieser Reihenfolge durch:

| Notebook | Inhalt |
| --- | --- |
| `00_setup_check.ipynb` | Prueft Installation, interaktive Plots und Bedienelemente |
| `01_EELS_modeling.ipynb` | EELS: ausrichten, Untergrund, Kantenmodell, Feinstruktur |
| `02_EDX_modeling.ipynb` | EDX: Linienauswahl, Modellfit, Untergrundfenster |
| `03_EELS_praktikum_auswertung.ipynb` | EELS an einer Lamelle, Ca-Speziation *(braucht Zusatzdaten, siehe unten)* |

**Starte die Notebooks immer ueber `pixi run lab`.** Wenn du JupyterLab anders
startest (z.B. ein systemweit installiertes Jupyter), benutzt es das falsche Python
und keines der Pakete ist da.

---

## Wenn etwas nicht funktioniert

<details>
<summary><b>"pixi: Befehl nicht gefunden" / "pixi is not recognized"</b></summary>

Terminal bzw. PowerShell nach der Installation **komplett schliessen und neu oeffnen**.
Der Installer traegt pixi in den Suchpfad ein, das wirkt erst in einer neuen Sitzung.

Hilft das nicht, ruf pixi mit vollem Pfad auf:

- Windows: `%USERPROFILE%\.pixi\bin\pixi.exe --version`
- macOS/Linux: `~/.pixi/bin/pixi --version`

</details>

<details>
<summary><b>Plots bleiben leer oder es erscheint nur ein grauer Kasten</b></summary>

Das interaktive Matplotlib-Backend (`ipympl`) laeuft nicht. Ersetze in der obersten
Codezelle des Notebooks

```python
%matplotlib widget
```

durch

```python
%matplotlib inline
```

und starte den Kernel neu (Menue **Kernel -> Restart Kernel and Run All Cells**).
Die Plots sind dann statisch, aber inhaltlich identisch.

</details>

<details>
<summary><b><code>m.gui()</code> zeigt nur Text statt Schiebereglern</b></summary>

Kein Problem: unter jeder `m.gui()`-Zelle steht eine **Variante B**, die dasselbe
per Code macht. Benutze die.

</details>

<details>
<summary><b><code>ModuleNotFoundError: No module named 'hyperspy'</code></b></summary>

Du hast JupyterLab nicht ueber `pixi run lab` gestartet. Schliesse es und starte es
mit diesem Befehl neu.

</details>

<details>
<summary><b><code>FileNotFoundError</code> beim Laden der Daten</b></summary>

Die Fehlermeldung sagt dir, welcher Pfad erwartet wurde und was stattdessen in `data/`
liegt. Meistens ist beim Entpacken eine Ordnerebene zu viel entstanden - vergleiche
mit dem Ordnerbaum in Schritt 3.

Zum Nachschauen, was gefunden wird:

```bash
pixi run python -c "import sys; sys.path.insert(0,'notebooks'); import workshop_data; workshop_data.status()"
```

</details>

<details>
<summary><b>Der Fit laeuft ewig</b></summary>

`multifit` fittet jeden Bildpunkt einzeln. Erhoehe den `rebin`-Faktor, z.B. von
`scale=[2, 2, 1]` auf `[4, 4, 1]` - das viertelt die Zahl der Bildpunkte.

</details>

<details>
<summary><b>Alles auf Anfang</b></summary>

```bash
pixi clean
pixi install
```

Loescht die Umgebung und baut sie aus `pixi.lock` neu auf. Deine Notebooks und Daten
bleiben unangetastet.

</details>

---

## Fuer Betreuende

### Aufbau

```
pixi.toml            Paketliste (von Hand gepflegt)
pixi.lock            exakte Versionen aller Pakete, alle 4 Plattformen - NICHT von Hand aendern
check_setup.py       Setup-Pruefung, auch als 'pixi run check'
notebooks/
  workshop_data.py   plattformunabhaengige Datensuche mit brauchbaren Fehlermeldungen
  0*.ipynb           die Workshop-Notebooks
data/                Messdaten, per .gitignore ausgeschlossen
```

### Versionen

Festgeschrieben in `pixi.lock` fuer `linux-64`, `win-64`, `osx-64` und `osx-arm64`:
HyperSpy 2.4.0, eXSpy 0.3.2, RosettaSciIO 0.14.0, NumPy 2.4.6, SciPy 1.18.0,
Matplotlib 3.10.9, Python 3.12.

**Matplotlib ist bewusst auf `<3.11` gepinnt.** HyperSpy 2.4.0 uebergibt
Marker-Farben in einem Format, das Matplotlib 3.11 elementweise zerlegt; der
Aufruf `plot(background_windows=...)` in Notebook 02 stirbt dann mit
`ValueError: Invalid RGBA argument`. Getestet: mit 3.10.9 laeuft er durch.
Den Pin erst loesen, wenn ein HyperSpy-Release das behoben hat - und dann
Notebook 02 wirklich einmal durchlaufen lassen.

### Datensaetze

| Ordner | Groesse | Wofuer | Im Teilnehmenden-ZIP |
| --- | --- | --- | --- |
| `data/nanopore/` | 152 MB (ZIP: 43 MB) | Notebook 01 + 02 | ja |
| `data/praktikum/` | ~320 MB | Notebook 03 (Lamelle, Ca-Referenzen) | nein |

In `notebooks/workshop_data.py` regelt das Set `OPTIONAL`, welche Datensaetze
fehlen duerfen, ohne dass `pixi run check` einen Fehler meldet.

Paket hinzufuegen:

```bash
pixi add <paketname>     # aktualisiert pixi.toml und pixi.lock
```

**`pixi.lock` gehoert mit ins Git-Repository** - sie ist der Grund, warum alle
dieselbe Umgebung bekommen.

### Neue Datensaetze einbinden

In `notebooks/workshop_data.py` das Dictionary `DATASETS` erweitern:

```python
DATASETS = {
    "mein_datensatz": "unterordner/Meine Datei.dm4",
    ...
}
```

Danach im Notebook `load("mein_datensatz")`. Nie feste Pfade ins Notebook schreiben -
die brechen auf dem naechsten Rechner.

### Vor der Verteilung

Notebook-Ausgaben leeren, bevor committet wird - sonst wachsen die Dateien auf
Megabytegroesse und die Diffs werden unbrauchbar:

```bash
pixi run jupyter nbconvert --clear-output --inplace notebooks/*.ipynb
```
