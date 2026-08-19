"""Locate the workshop measurement data - cross-platform and fault-tolerant.

The notebooks never hard-code a path. They do this instead::

    from workshop_data import load
    signal = load("eels_highloss")

That way the same notebooks run unchanged on Windows, macOS and Linux.
If the data sits in the wrong place, the error message states exactly what was
expected where, and what was found instead.
"""

from pathlib import Path

# Where the data belongs: <project folder>/data/
# __file__ is notebooks/workshop_data.py, so two levels up is the project folder.
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

# Logical name -> path below data/, matching how the ZIP unpacks.
DATASETS = {
    # Nanopore dataset (EELS + EDX modelling)
    "eels_highloss": "nanopore/EELS Spectrum Image (high-loss).dm4",
    "eels_lowloss": "nanopore/EELS Spectrum Image (low-loss).dm4",
    "edx_si": "nanopore/EDS Spectrum Image.dm4",
    "adf": "nanopore/ADF Image.dm4",
    "adf_survey": "nanopore/ADF Image (SI Survey).dm4",
    "si_standards": "nanopore/Si Standards",  # folder of reference spectra
    # Lamella dataset - optional, see OPTIONAL below
    "lamella_eels_highloss": "lamella/EELS HL SI.dm4",
    "lamella_eels_lowloss": "lamella/EELS LL SI.dm4",
    "lamella_adf": "lamella/JEOL Image.dm4",
    "ca_standards": "lamella/Ca Standards",  # folder of Ca reference spectra
}

# These datasets are not part of the participant ZIP (which holds 'nanopore' only).
# Only notebook 03 needs them. If they are missing that is not an error -
# 'pixi run check' reports them as a note.
OPTIONAL = {
    "lamella_eels_highloss",
    "lamella_eels_lowloss",
    "lamella_adf",
    "ca_standards",
}

DOWNLOAD_HINT = (
    "How to fix this:\n"
    "  1. Download the data ZIP (link is in the README).\n"
    "  2. Unpack it so that the 'nanopore' folder sits DIRECTLY\n"
    f"     inside this folder:\n     {DATA_DIR}\n"
    "  3. Run this cell again.\n\n"
    "Most common mistake: one folder level too many, i.e.\n"
    "  data/measurements/nanopore/...   instead of   data/nanopore/...\n"
    "(This script usually finds it anyway - but the clean layout is better.)"
)


def _describe_data_dir():
    """Readable description of what is currently in data/ - for error messages."""
    if not DATA_DIR.exists():
        return f"The 'data' folder does not exist:\n    {DATA_DIR}"
    entries = sorted(p.name + ("/" if p.is_dir() else "") for p in DATA_DIR.iterdir())
    if not entries:
        return f"The 'data' folder is empty:\n    {DATA_DIR}"
    shown = entries[:15]
    rest = f"\n    ... and {len(entries) - 15} more" if len(entries) > 15 else ""
    return f"{DATA_DIR} currently contains:\n    " + "\n    ".join(shown) + rest


def _search_by_name(target_name):
    """Search recursively for the file name - catches badly unpacked ZIPs."""
    if not DATA_DIR.exists():
        return []
    hits = [p for p in DATA_DIR.rglob(target_name) if p.exists()]
    # Shortest path first: the least deeply nested candidate wins.
    return sorted(hits, key=lambda p: len(p.parts))


def path(name):
    """Return the path to a dataset (without loading it).

    Parameters
    ----------
    name : str
        Logical name from DATASETS, e.g. "eels_highloss".

    Returns
    -------
    pathlib.Path
    """
    if name not in DATASETS:
        raise KeyError(
            f"Unknown dataset {name!r}.\n"
            f"Available: {', '.join(sorted(DATASETS))}"
        )

    expected = DATA_DIR / DATASETS[name]
    if expected.exists():
        return expected

    # Plan B: search anywhere below data/ for the file name.
    target_name = Path(DATASETS[name]).name
    hits = _search_by_name(target_name)
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        listing = "\n    ".join(str(p) for p in hits[:5])
        raise FileNotFoundError(
            f"{target_name!r} occurs more than once below data/ - cannot tell which one is meant:\n"
            f"    {listing}\n\n"
            f"Delete the duplicates, or put the file at:\n    {expected}"
        )

    raise FileNotFoundError(
        f"Dataset {name!r} not found.\n\n"
        f"Expected at:\n    {expected}\n\n"
        f"{_describe_data_dir()}\n\n"
        f"{DOWNLOAD_HINT}"
    )


def load(name, **kwargs):
    """Load a dataset with HyperSpy.

    Extra arguments (e.g. ``signal_type="EELS"``) are passed straight through to
    ``hyperspy.api.load``.
    """
    import hyperspy.api as hs

    return hs.load(str(path(name)), **kwargs)


def load_standards(name="si_standards", sigma=None):
    """Load every reference spectrum in a folder as ``{name: signal}``.

    Parameters
    ----------
    name : str
        Logical name of a folder dataset.
    sigma : float, optional
        If given, each spectrum is smoothed with a Gaussian of this width
        (along the energy axis).
    """
    import hyperspy.api as hs

    folder = path(name)
    if not folder.is_dir():
        raise NotADirectoryError(f"{folder} is not a folder.")

    standards = {}
    for file in sorted(folder.iterdir()):
        if not file.is_file() or file.name.startswith("."):
            continue
        try:
            s = hs.load(str(file))
        except Exception as error:  # e.g. a README sitting in the folder
            print(f"  skipped: {file.name} ({error})")
            continue
        if sigma is not None:
            from scipy.ndimage import gaussian_filter1d

            s.data = gaussian_filter1d(s.data, sigma=sigma, axis=-1)
        standards[file.stem] = s

    if not standards:
        raise FileNotFoundError(f"No loadable spectra found in {folder}.")
    return standards


def status():
    """Report which datasets can be found - used by the setup check."""
    print(f"Data folder: {DATA_DIR}\n")
    missing_required, missing_optional = [], []
    for name in sorted(DATASETS):
        tag = " (optional)" if name in OPTIONAL else ""
        try:
            p = path(name)
            print(f"  [ok]      {name:26s} -> {p.relative_to(DATA_DIR)}")
        except FileNotFoundError:
            print(f"  [missing] {name:26s}{tag}")
            (missing_optional if name in OPTIONAL else missing_required).append(name)
    print()

    if missing_optional:
        print(
            f"{len(missing_optional)} optional datasets are missing. That is normal:\n"
            "they belong to notebook 03 and are not part of the participant ZIP.\n"
            "Notebooks 01 and 02 work without them.\n"
        )

    if missing_required:
        print(f"{len(missing_required)} required datasets are missing.\n")
        print(DOWNLOAD_HINT)
        return False

    print("All required datasets found.")
    return True
