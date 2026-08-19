# Hier kommen die Messdaten hin

Dieser Ordner ist absichtlich leer. Die `.dm4`-Dateien sind mehrere hundert Megabyte
gross und liegen deshalb nicht im Repository.

**Download-Link:** <HIER DEN DOWNLOAD-LINK EINTRAGEN>

Entpacke das ZIP so, dass der Ordner `nanopore` **direkt hier** liegt:

```
data/
├── README.md                 <- diese Datei
└── nanopore/
    ├── EELS Spectrum Image (high-loss).dm4
    ├── EELS Spectrum Image (low-loss).dm4
    ├── EDS Spectrum Image.dm4
    ├── ADF Image.dm4
    ├── ADF Image (SI Survey).dm4
    └── Si Standards/
```

Das reicht fuer die Notebooks 00, 01 und 02.

Notebook 03 braucht zusaetzlich `data/praktikum/` (Lamellen-Datensatz mit den
Ca-Referenzspektren). Der ist nicht im ZIP - wenn er fehlt, ist das kein Fehler.

Nicht so (eine Ordnerebene zu viel - der haeufigste Fehler):

```
data/
└── messdaten/
    └── nanopore/
```

Pruefen, ob alles gefunden wird:

```bash
pixi run check
```
