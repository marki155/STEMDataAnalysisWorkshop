"""Prueft vor dem Workshop, ob alles bereit ist.

Aufruf:   pixi run check
"""

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR / "notebooks"))

probleme = []


def abschnitt(titel):
    print()
    print(titel)
    print("-" * len(titel))


print("=" * 60)
print("Setup-Check: STEM Data Analysis Workshop")
print("=" * 60)

abschnitt("1. Pakete")
try:
    import hyperspy
    import exspy
    import rsciio
    import numpy
    import scipy
    import matplotlib
    import ipympl
    import hyperspy_gui_ipywidgets

    for name, modul in [
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
        version = sys.version.split()[0] if modul is None else modul.__version__
        print(f"  [ok] {name:24s} {version}")
except ImportError as fehler:
    print(f"  [FEHLER] {fehler}")
    probleme.append(
        "Ein Paket fehlt. Starte die Notebooks ueber 'pixi run lab', nicht ueber "
        "ein anderes Python."
    )

abschnitt("2. dm3/dm4-Leser")
try:
    from rsciio import IO_PLUGINS

    formate = {f.lower() for p in IO_PLUGINS for f in p.get("file_extensions", [])}
    if {"dm3", "dm4"} <= formate:
        print("  [ok] .dm3 und .dm4 koennen gelesen werden")
    else:
        print("  [FEHLER] dm3/dm4-Leser nicht registriert")
        probleme.append("RosettaSciIO kennt das Gatan-Format nicht.")
except Exception as fehler:
    print(f"  [FEHLER] {fehler}")
    probleme.append(str(fehler))

abschnitt("3. EELS-/EDX-Signaltypen (exspy)")
try:
    import numpy as np
    import hyperspy.api as hs
    import exspy  # noqa: F401  - registriert die Signaltypen

    for signaltyp, erwartet in [("EELS", "EELSSpectrum"), ("EDS_TEM", "EDSTEMSpectrum")]:
        s = hs.signals.Signal1D(np.zeros((2, 2, 50)))
        s.set_signal_type(signaltyp)
        if type(s).__name__ == erwartet:
            print(f"  [ok] {signaltyp:8s} -> {erwartet}")
        else:
            print(f"  [FEHLER] {signaltyp} -> {type(s).__name__}, erwartet {erwartet}")
            probleme.append(f"Signaltyp {signaltyp} wird nicht erkannt.")
except Exception as fehler:
    print(f"  [FEHLER] {fehler}")
    probleme.append(str(fehler))

abschnitt("4. GOSH-Datenbank (fuer EELS-Kantenmodelle, ~42 MB)")
print("  Wird beim ersten EELS-Modell aus dem Netz geladen und dauerhaft")
print("  zwischengespeichert. Jetzt holen spart WLAN-Aerger im Workshop.")
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
    print("  [ok] GOSH-Datenbank ist lokal verfuegbar")
except Exception as fehler:
    print(f"  [WARNUNG] {type(fehler).__name__}: {fehler}")
    print("  Ohne Internet funktionieren EELS-Kantenmodelle nicht.")

abschnitt("5. Messdaten")
try:
    import workshop_data

    if not workshop_data.status():
        probleme.append("Es fehlen Messdaten (siehe oben).")
except Exception as fehler:
    print(f"  [FEHLER] {fehler}")
    probleme.append(str(fehler))

print()
print("=" * 60)
if probleme:
    print(f"{len(probleme)} Punkt(e) offen:")
    for p in probleme:
        print(f"  - {p}")
    sys.exit(1)
print("Alles bereit. Starte den Workshop mit:  pixi run lab")
print("=" * 60)
