"""Findet die Messdaten des Workshops - plattformunabhaengig und fehlertolerant.

Die Notebooks laden Daten nie ueber einen festen Pfad, sondern so::

    from workshop_data import load
    signal = load("eels_highloss")

Damit laufen dieselben Notebooks unveraendert unter Windows, macOS und Linux.
Liegen die Daten falsch, sagt die Fehlermeldung konkret, was wo erwartet wurde
und was stattdessen gefunden wurde.
"""

from pathlib import Path

# Wo die Daten liegen sollen: <Projektordner>/data/
# __file__ ist notebooks/workshop_data.py -> zwei Ebenen hoch ist der Projektordner.
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

# Logischer Name -> Pfad unterhalb von data/, so wie das ZIP entpackt wird.
DATASETS = {
    # Nanopore-Datensatz (EELS + EDX Modeling)
    "eels_highloss": "nanopore/EELS Spectrum Image (high-loss).dm4",
    "eels_lowloss": "nanopore/EELS Spectrum Image (low-loss).dm4",
    "edx_si": "nanopore/EDS Spectrum Image.dm4",
    "adf": "nanopore/ADF Image.dm4",
    "adf_survey": "nanopore/ADF Image (SI Survey).dm4",
    "si_standards": "nanopore/Si Standards",  # Ordner mit Referenzspektren
    # Praktikums-Datensatz
    "praktikum_eels_highloss": "praktikum/EELS HL SI.dm4",
    "praktikum_eels_lowloss": "praktikum/EELS LL SI.dm4",
    "praktikum_adf": "praktikum/JEOL Image.dm4",
}

DOWNLOAD_HINT = (
    "So behebst du das:\n"
    "  1. Lade das Daten-ZIP herunter (Link steht in der README).\n"
    "  2. Entpacke es so, dass die Ordner 'nanopore' und 'praktikum'\n"
    f"     DIREKT in diesem Ordner liegen:\n     {DATA_DIR}\n"
    "  3. Fuehre diese Zelle erneut aus.\n\n"
    "Haeufigster Fehler: ein Ordner zu viel, also\n"
    "  data/messdaten/nanopore/...   statt   data/nanopore/...\n"
    "(Das findet dieses Skript zwar meistens trotzdem - aber sauberer ist es so.)"
)


def _describe_data_dir():
    """Beschreibt lesbar, was gerade in data/ liegt - fuer Fehlermeldungen."""
    if not DATA_DIR.exists():
        return f"Der Ordner 'data' existiert nicht:\n    {DATA_DIR}"
    eintraege = sorted(p.name + ("/" if p.is_dir() else "") for p in DATA_DIR.iterdir())
    if not eintraege:
        return f"Der Ordner 'data' ist leer:\n    {DATA_DIR}"
    gezeigt = eintraege[:15]
    rest = f"\n    ... und {len(eintraege) - 15} weitere" if len(eintraege) > 15 else ""
    return (
        f"In {DATA_DIR} liegt aktuell:\n    " + "\n    ".join(gezeigt) + rest
    )


def _search_by_name(zielname):
    """Sucht rekursiv nach dem Dateinamen - faengt falsch entpackte ZIPs ab."""
    if not DATA_DIR.exists():
        return []
    treffer = [p for p in DATA_DIR.rglob(zielname) if p.exists()]
    # Kuerzeste Pfade zuerst: die am wenigsten verschachtelte Variante gewinnt.
    return sorted(treffer, key=lambda p: len(p.parts))


def path(name):
    """Gibt den Pfad zu einem Datensatz zurueck (ohne ihn zu laden).

    Parameters
    ----------
    name : str
        Logischer Name aus DATASETS, z.B. "eels_highloss".

    Returns
    -------
    pathlib.Path
    """
    if name not in DATASETS:
        raise KeyError(
            f"Unbekannter Datensatz {name!r}.\n"
            f"Verfuegbar sind: {', '.join(sorted(DATASETS))}"
        )

    erwartet = DATA_DIR / DATASETS[name]
    if erwartet.exists():
        return erwartet

    # Plan B: irgendwo unterhalb von data/ nach dem Dateinamen suchen.
    zielname = Path(DATASETS[name]).name
    treffer = _search_by_name(zielname)
    if len(treffer) == 1:
        return treffer[0]
    if len(treffer) > 1:
        liste = "\n    ".join(str(p) for p in treffer[:5])
        raise FileNotFoundError(
            f"{zielname!r} kommt mehrfach unter data/ vor - ich weiss nicht, welche gemeint ist:\n"
            f"    {liste}\n\n"
            f"Loesche die Duplikate oder lege die Datei nach:\n    {erwartet}"
        )

    raise FileNotFoundError(
        f"Datensatz {name!r} nicht gefunden.\n\n"
        f"Erwartet wurde:\n    {erwartet}\n\n"
        f"{_describe_data_dir()}\n\n"
        f"{DOWNLOAD_HINT}"
    )


def load(name, **kwargs):
    """Laedt einen Datensatz mit HyperSpy.

    Zusaetzliche Argumente (z.B. ``signal_type="EELS"``) werden an
    ``hyperspy.api.load`` durchgereicht.
    """
    import hyperspy.api as hs

    return hs.load(str(path(name)), **kwargs)


def load_standards(name="si_standards", sigma=None):
    """Laedt alle Referenzspektren aus einem Ordner als ``{Name: Signal}``.

    Parameters
    ----------
    name : str
        Logischer Name eines Ordner-Datensatzes.
    sigma : float, optional
        Wenn gesetzt, wird jedes Spektrum mit einem Gauss dieser Breite
        geglaettet (entlang der Energieachse).
    """
    import hyperspy.api as hs

    ordner = path(name)
    if not ordner.is_dir():
        raise NotADirectoryError(f"{ordner} ist kein Ordner.")

    standards = {}
    for datei in sorted(ordner.iterdir()):
        if not datei.is_file() or datei.name.startswith("."):
            continue
        try:
            s = hs.load(str(datei))
        except Exception as fehler:  # z.B. eine README im Ordner
            print(f"  uebersprungen: {datei.name} ({fehler})")
            continue
        if sigma is not None:
            from scipy.ndimage import gaussian_filter1d

            s.data = gaussian_filter1d(s.data, sigma=sigma, axis=-1)
        standards[datei.stem] = s

    if not standards:
        raise FileNotFoundError(f"Keine ladbaren Spektren in {ordner} gefunden.")
    return standards


def status():
    """Zeigt an, welche Datensaetze gefunden werden - fuer den Setup-Check."""
    print(f"Datenordner: {DATA_DIR}\n")
    fehlend = []
    for name in sorted(DATASETS):
        try:
            p = path(name)
            print(f"  [ok]     {name:26s} -> {p.relative_to(DATA_DIR)}")
        except FileNotFoundError:
            print(f"  [fehlt]  {name:26s}")
            fehlend.append(name)
    print()
    if fehlend:
        print(f"{len(fehlend)} von {len(DATASETS)} Datensaetzen fehlen.\n")
        print(DOWNLOAD_HINT)
    else:
        print("Alle Datensaetze gefunden.")
    return not fehlend
