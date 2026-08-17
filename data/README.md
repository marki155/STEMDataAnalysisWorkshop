# Hier kommen die Messdaten hin

Dieser Ordner ist absichtlich leer. Die `.dm4`-Dateien sind mehrere hundert Megabyte
gross und liegen deshalb nicht im Repository.

**Download-Link:** <HIER DEN DOWNLOAD-LINK EINTRAGEN>

Entpacke das ZIP so, dass die Ordner `nanopore` und `praktikum` **direkt hier** liegen:

```
data/
├── README.md                 <- diese Datei
├── nanopore/
│   ├── EELS Spectrum Image (high-loss).dm4
│   ├── EELS Spectrum Image (low-loss).dm4
│   ├── EDS Spectrum Image.dm4
│   ├── ADF Image.dm4
│   ├── ADF Image (SI Survey).dm4
│   └── Si Standards/
└── praktikum/
    ├── EELS HL SI.dm4
    ├── EELS LL SI.dm4
    └── JEOL Image.dm4
```

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
