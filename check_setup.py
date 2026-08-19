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

section("1. Packages")
try:
    import hyperspy
    import exspy
    import rsciio
    import numpy
    import scipy
    import matplotlib
    import ipympl
    import hyperspy_gui_ipywidgets

    for name, module in [
        ("Python", None),
        ("hyperspy", hyperspy),
        ("exspy", exspy),
        ("rosettasciio", rsciio),
        ("numpy", numpy),
        ("scipy", scipy),
        ("matplotlib", matplotlib),
        ("ipympl", ipympl),
        ("hyperspy-gui-ipywidgets", hyperspy_gui_ipywidgets),
    ]:
        version = sys.version.split()[0] if module is None else module.__version__
        print(f"  [ok] {name:24s} {version}")
except ImportError as error:
    print(f"  [FAILED] {error}")
    problems.append(
        "A package is missing. Start the notebooks with 'pixi run lab', not with "
        "some other Python."
    )

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
