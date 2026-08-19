"""Locate the workshop measurement data - cross-platform and fault-tolerant.

The notebooks never hard-code a path. They do this instead::

    from workshop_data import load
    signal = load("eels_highloss")

That way the same notebooks run unchanged on Windows, macOS and Linux.
If the data sits in the wrong place, the error message states exactly what was
expected where, and what was found instead.

For your own measurements there are two routes:

* ``load_path("my_folder/My File.dm4")`` loads any file below ``data/`` directly,
  without registering it first. Good for trying things out.
* Adding an entry to :data:`DATASETS` gives the file a short logical name that
  works in every notebook. Better once you use the file more than once.

Use :func:`list_files` to see what is actually there, and
:func:`check_elements` before building a model - it catches elements whose edges
do not fall inside the measured energy range at all.
"""

import fnmatch
import os
from pathlib import Path

# Where the data belongs: <project folder>/data/
# __file__ is notebooks/workshop_data.py, so two levels up is the project folder.
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

# Logical name -> path below data/, matching how the ZIP unpacks.
#
# To add your own measurement, put the file below data/ and add a line here:
#     "my_sample_eels": "my_sample/EELS Spectrum Image.dm4",
# After that, load("my_sample_eels") works in any notebook.
DATASETS = {
    # Nanopore dataset (EELS + EDX modelling)
    "eels_highloss": "nanopore/EELS Spectrum Image (high-loss).dm4",
    "eels_lowloss": "nanopore/EELS Spectrum Image (low-loss).dm4",
    "edx_si": "nanopore/EDS Spectrum Image.dm4",
    "adf": "nanopore/ADF Image.dm4",
    "adf_survey": "nanopore/ADF Image (SI Survey).dm4",
    "si_standards": "nanopore/Si Standards",  # folder of reference spectra
}

# Datasets that may be missing without 'pixi run check' reporting an error.
# Add your own entries here if they are not part of the shared data ZIP.
OPTIONAL = set()

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


def _walk_data(pattern="*"):
    """Every file below data/ matching a glob pattern.

    Uses os.walk with followlinks=True on purpose: data/nanopore is often a
    symlink to the real storage location, and Path.rglob would not descend into
    it - which would make this silently return nothing.
    """
    if not DATA_DIR.exists():
        return []
    found = []
    for root, _dirs, files in os.walk(DATA_DIR, followlinks=True):
        for name in files:
            full = Path(root) / name
            relative = full.relative_to(DATA_DIR)
            if fnmatch.fnmatch(str(relative), pattern) or fnmatch.fnmatch(name, pattern):
                found.append(full)
    return sorted(found)


def _search_by_name(target_name):
    """Search recursively for the file name - catches badly unpacked ZIPs."""
    hits = [p for p in _walk_data(target_name) if p.name == target_name]
    # Shortest path first: the least deeply nested candidate wins.
    return sorted(hits, key=lambda p: len(p.parts))


def path(name):
    """Return the path to a registered dataset (without loading it).

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
            f"Registered names: {', '.join(sorted(DATASETS))}\n\n"
            "For a file that is not registered, use load_path(\"folder/file.dm4\"),\n"
            "or add a line to DATASETS in notebooks/workshop_data.py.\n"
            "list_files() shows what is available."
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


def resolve(relative_path):
    """Turn a path relative to ``data/`` into a real path, with a helpful error.

    Unlike :func:`path` this needs no entry in DATASETS - point it straight at a
    file you dropped into ``data/``::

        resolve("my_sample/EELS SI.dm4")
    """
    candidate = DATA_DIR / relative_path
    if candidate.exists():
        return candidate

    hits = _search_by_name(Path(relative_path).name)
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        listing = "\n    ".join(str(p) for p in hits[:5])
        raise FileNotFoundError(
            f"{Path(relative_path).name!r} occurs more than once below data/:\n    {listing}\n\n"
            "Give a more specific path."
        )

    raise FileNotFoundError(
        f"Not found:\n    {candidate}\n\n"
        f"{_describe_data_dir()}\n\n"
        "list_files() shows every file below data/."
    )


def list_files(pattern="*", max_rows=60):
    """Print every file below ``data/`` - use this to find your own measurements.

    Parameters
    ----------
    pattern : str
        Glob pattern, e.g. ``"*.dm4"`` or ``"my_sample/*"``.
    max_rows : int
        Stop after this many rows.
    """
    if not DATA_DIR.exists():
        print(f"The 'data' folder does not exist yet:\n    {DATA_DIR}")
        return []

    files = _walk_data(pattern)
    if not files:
        print(f"No file below {DATA_DIR} matches {pattern!r}.")
        return []

    print(f"{len(files)} file(s) below {DATA_DIR}:\n")
    for p in files[:max_rows]:
        size = p.stat().st_size
        unit = f"{size / 1e6:8.1f} MB" if size >= 1e6 else f"{size / 1e3:8.1f} kB"
        print(f"  {unit}   {p.relative_to(DATA_DIR)}")
    if len(files) > max_rows:
        print(f"  ... and {len(files) - max_rows} more")
    print('\nLoad one with:  load_path("<the path shown above>")')
    return [p.relative_to(DATA_DIR) for p in files]


def load(name, **kwargs):
    """Load a registered dataset with HyperSpy.

    Extra arguments (e.g. ``signal_type="EELS"``) are passed straight through to
    ``hyperspy.api.load``.
    """
    import hyperspy.api as hs

    return hs.load(str(path(name)), **kwargs)


def load_path(relative_path, **kwargs):
    """Load any file below ``data/`` by its relative path.

    No entry in DATASETS needed::

        signal = load_path("my_sample/EELS SI.dm4", signal_type="EELS")
    """
    import hyperspy.api as hs

    return hs.load(str(resolve(relative_path)), **kwargs)


def load_standards(name="si_standards", sigma=None, folder=None):
    """Load every reference spectrum in a folder as ``{name: signal}``.

    Parameters
    ----------
    name : str
        Logical name of a registered folder dataset. Ignored if ``folder`` is given.
    sigma : float, optional
        If given, each spectrum is smoothed with a Gaussian of this width
        (along the energy axis).
    folder : str, optional
        Path relative to ``data/``, for a folder that is not registered.
    """
    import hyperspy.api as hs

    directory = resolve(folder) if folder is not None else path(name)
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} is not a folder.")

    standards = {}
    for file in sorted(directory.iterdir()):
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
        raise FileNotFoundError(f"No loadable spectra found in {directory}.")
    return standards


def energy_range(signal):
    """Return ``(first, last)`` energy of a spectrum's signal axis, in eV."""
    axis = signal.axes_manager[-1]
    return float(axis.offset), float(axis.offset + axis.size * axis.scale)


def check_elements(signal, elements, verbose=True):
    """Report which elements actually have an EELS edge in the measured range.

    This exists because of a trap that costs real time: ``add_elements`` accepts
    any element, and elements whose edges lie outside the recorded energy window
    are then dropped **without any error or warning**. The notebook runs happily
    and the results are meaningless.

    Call this before building a model.

    Parameters
    ----------
    signal : hyperspy signal
        The (EELS) signal you are about to model.
    elements : list of str
        The elements you intend to pass to ``add_elements``.

    Returns
    -------
    dict
        ``{"usable": [...], "unusable": [...], "edges": {element: [(name, eV), ...]}}``
    """
    from exspy.material import elements as element_db

    low, high = energy_range(signal)
    usable, unusable, edges = [], [], {}

    for element in elements:
        try:
            # The database is a DictionaryTreeBrowser, so convert before iterating.
            binding = element_db[element]["Atomic_properties"]["Binding_energies"].as_dictionary()
        except (KeyError, AttributeError):
            unusable.append(element)
            edges[element] = []
            continue
        inside = sorted(
            (name, float(info["onset_energy (eV)"]))
            for name, info in binding.items()
            if low <= float(info["onset_energy (eV)"]) <= high
        )
        edges[element] = inside
        (usable if inside else unusable).append(element)

    if verbose:
        print(f"Measured range: {low:.0f} - {high:.0f} eV\n")
        for element in elements:
            inside = edges[element]
            if inside:
                shown = ", ".join(f"{n}={e:.0f} eV" for n, e in inside[:4])
                print(f"  [ok]      {element:3s} {shown}")
            else:
                try:
                    binding = element_db[element]["Atomic_properties"][
                        "Binding_energies"
                    ].as_dictionary()
                    nearest = sorted(
                        (float(i["onset_energy (eV)"]), n) for n, i in binding.items()
                    )[:3]
                    hint = ", ".join(f"{n}={e:.0f} eV" for e, n in nearest)
                except (KeyError, AttributeError):
                    hint = "no data for this element"
                print(f"  [NO EDGE] {element:3s} nearest edges: {hint}")
        if unusable:
            print(
                f"\n{len(unusable)} element(s) have no edge in this range: "
                f"{', '.join(unusable)}\n"
                "add_elements would drop them silently. Remove them from the list."
            )
        else:
            print("\nAll elements have at least one edge in the measured range.")

    return {"usable": usable, "unusable": unusable, "edges": edges}


def check_background_window(signal, signal_range):
    """Check that a background window lies inside the data and before the first edge.

    ``remove_background`` does not complain when the window sits outside the
    recorded range - it just returns something meaningless.
    """
    low, high = energy_range(signal)
    start, stop = float(signal_range[0]), float(signal_range[1])

    if stop <= low or start >= high:
        print(
            f"[PROBLEM] The window {start:.0f}-{stop:.0f} eV lies completely outside\n"
            f"          the measured range {low:.0f}-{high:.0f} eV."
        )
        return False
    if start < low or stop > high:
        print(
            f"[WARNING] The window {start:.0f}-{stop:.0f} eV only partly overlaps\n"
            f"          the measured range {low:.0f}-{high:.0f} eV."
        )
        return False
    print(f"[ok] Window {start:.0f}-{stop:.0f} eV lies inside {low:.0f}-{high:.0f} eV.")
    return True


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
            f"{len(missing_optional)} optional datasets are missing - that is not an error.\n"
        )

    if missing_required:
        print(f"{len(missing_required)} required datasets are missing.\n")
        print(DOWNLOAD_HINT)
        return False

    print("All required datasets found.")
    return True
