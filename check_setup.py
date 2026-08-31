"""Check before the workshop that everything is ready.

Run with:   pixi run check
"""

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR / "notebooks"))

problems = []


def section(title):
    print()
    print(title)
    print("-" * len(title))


print("=" * 60)
print("Setup check: STEM Data Analysis Workshop")
print("=" * 60)

SYNC_FOLDERS = ("onedrive", "dropbox", "google drive", "googledrive", "icloud", "nextcloud")


def explain_dll_failure(module_name, error):
    """Windows: a package imports but its compiled part will not load."""
    env = Path(sys.prefix)
    print()
    print(f"  This is not a missing package - {module_name} is installed, but a compiled")
    print("  file next to it could not be loaded. On Windows that has a short list of causes.")
    print()

    synced = [folder for folder in SYNC_FOLDERS if folder in str(env).lower()]
    if synced:
        print(f"  1. THE ENVIRONMENT SITS INSIDE A SYNCED FOLDER ({synced[0]}).")
        print(f"     {env}")
        print("     This is the usual cause. With Files On-Demand the DLL is only a")
        print("     placeholder on disk until something opens it, and Windows cannot load")
        print("     a placeholder as a library. Sync can also lock or quarantine files")
        print("     while it works.")
        print()
        print("     Fix, best first:")
        print("       - Move the whole project out of the synced folder, e.g. to")
        print("         C:\\Users\\<you>\\Projects\\STEMDataAnalysisWorkshop, then")
        print("         'pixi install' again. A 2 GB environment does not belong in cloud")
        print("         sync anyway - it is rebuilt from pixi.lock in minutes.")
        print("       - Or right-click the .pixi folder -> 'Always keep on this device',")
        print("         wait for the sync to finish, then try again.")
        print("       - Or exclude .pixi from syncing in the client's settings.")
    else:
        print("  1. Environment location looks fine (not inside a sync folder):")
        print(f"     {env}")

    longest = 0
    try:
        for path in env.rglob("*.dll"):
            longest = max(longest, len(str(path)))
    except OSError:
        pass
    print()
    if longest == 0:
        print("  2. Path length: could not scan the environment for DLLs, so this was")
        print("     not checked. Windows cannot load a library whose full path exceeds")
        print("     260 characters; if yours is close to that, move the project to a")
        print("     shorter one such as C:\\Projects\\stem.")
    else:
        print(f"  2. Longest DLL path found: {longest} characters (Windows limit is 260).")
        if longest > 245:
            print("     TOO LONG. Move the project to a shorter path, e.g. C:\\Projects\\stem.")
        else:
            print("     Fine, this is not the cause.")

    print()
    print("  3. Another Python on PATH can supply a conflicting DLL. Check with:")
    print("       where python        (PowerShell: Get-Command python -All)")
    print("     Anything other than this environment should not come first. Always")
    print("     start through 'pixi run', never a system-wide python or conda.")
    print()
    print("  4. Antivirus may have quarantined the file. Check its log for the path above.")
    print()
    print("  5. If none of that applies, the package may have unpacked incompletely:")
    print("       pixi clean")
    print("       pixi install")


section("1. Packages")

MODULES = [
    ("hyperspy", "hyperspy"),
    ("exspy", "exspy"),
    ("rosettasciio", "rsciio"),
    ("numpy", "numpy"),
    ("scipy", "scipy"),
    ("matplotlib", "matplotlib"),
    ("ipympl", "ipympl"),
    ("hyperspy-gui-ipywidgets", "hyperspy_gui_ipywidgets"),
]

print(f"  [ok] {'Python':24s} {sys.version.split()[0]}")
print(f"       environment: {sys.prefix}")

import importlib

dll_failures = []
for label, module_name in MODULES:
    try:
        module = importlib.import_module(module_name)
    except ImportError as error:
        text = str(error)
        # Windows phrases this as "DLL load failed while importing X".
        if "DLL load failed" in text or "specified module could not be found" in text.lower():
            print(f"  [FAILED] {label:24s} DLL load failed")
            dll_failures.append((label, error))
        else:
            print(f"  [FAILED] {label:24s} {text}")
            problems.append(
                f"{label} is missing. Start the notebooks with 'pixi run lab', not with "
                "some other Python."
            )
        continue
    print(f"  [ok] {label:24s} {getattr(module, '__version__', 'unknown')}")

if dll_failures:
    for label, error in dll_failures:
        print()
        print(f"  --- {label}: {error}")
        explain_dll_failure(label, error)
    problems.append(
        f"{len(dll_failures)} package(s) failed with a DLL load error - see the notes above."
    )

# Warn about a synced folder even when nothing has broken yet.
_synced = [f for f in SYNC_FOLDERS if f in sys.prefix.lower()]
if _synced and not dll_failures:
    print()
    print(f"  [NOTE] This environment lives inside a {_synced[0]} folder:")
    print(f"         {sys.prefix}")
    print("         It works right now, but cloud sync and a 2 GB environment of compiled")
    print("         libraries are a poor match: sync can turn files into placeholders that")
    print("         Windows cannot load, which shows up later as 'DLL load failed'.")
    print("         Consider moving the project outside the synced folder and running")
    print("         'pixi install' again - it rebuilds from pixi.lock in minutes.")

section("2. dm3/dm4 reader")
try:
    from rsciio import IO_PLUGINS

    formats = {f.lower() for p in IO_PLUGINS for f in p.get("file_extensions", [])}
    if {"dm3", "dm4"} <= formats:
        print("  [ok] .dm3 and .dm4 can be read")
    else:
        print("  [FAILED] dm3/dm4 reader not registered")
        problems.append("RosettaSciIO does not know the Gatan format.")
except Exception as error:
    print(f"  [FAILED] {error}")
    problems.append(str(error))

section("3. EELS/EDX signal types (exspy)")
try:
    import numpy as np
    import hyperspy.api as hs
    import exspy  # noqa: F401  - registers the signal types

    for signal_type, expected in [("EELS", "EELSSpectrum"), ("EDS_TEM", "EDSTEMSpectrum")]:
        s = hs.signals.Signal1D(np.zeros((2, 2, 50)))
        s.set_signal_type(signal_type)
        if type(s).__name__ == expected:
            print(f"  [ok] {signal_type:8s} -> {expected}")
        else:
            print(f"  [FAILED] {signal_type} -> {type(s).__name__}, expected {expected}")
            problems.append(f"Signal type {signal_type} is not recognised.")
except Exception as error:
    print(f"  [FAILED] {error}")
    problems.append(str(error))

section("4. GOSH database (for EELS edge models, ~42 MB)")
print("  Downloaded from Zenodo the first time an EELS model is built, then")
print("  cached permanently. Fetching it now saves Wi-Fi trouble on the day.")
try:
    import numpy as np
    import hyperspy.api as hs
    import exspy  # noqa: F401

    s = hs.signals.Signal1D(np.ones((2, 2, 200)))
    s.set_signal_type("EELS")
    s.axes_manager[-1].offset = 90.0
    s.axes_manager[-1].scale = 0.5
    s.axes_manager[-1].units = "eV"
    s.set_microscope_parameters(
        beam_energy=200, convergence_angle=10, collection_angle=20
    )
    s.add_elements(["Si"])
    s.create_model(auto_background=False)
    print("  [ok] GOSH database is available locally")
except Exception as error:
    print(f"  [WARNING] {type(error).__name__}: {error}")
    print("  Without internet access, EELS edge models will not work.")

section("5. Measurement data")
try:
    import workshop_data

    if not workshop_data.status():
        problems.append("Measurement data is missing (see above).")
except Exception as error:
    print(f"  [FAILED] {error}")
    problems.append(str(error))

print()
print("=" * 60)
if problems:
    print(f"{len(problems)} item(s) still open:")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)
print("Everything ready. Start the workshop with:  pixi run lab")
print("=" * 60)
