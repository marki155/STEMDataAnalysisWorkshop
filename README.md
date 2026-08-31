# STEM Data Analysis Workshop

EELS and EDX analysis of STEM spectrum images with [HyperSpy](https://hyperspy.org)
and [eXSpy](https://hyperspy.org/exspy/).

These instructions assume **no Python knowledge**. Work through them top to bottom
and you will have a working environment in about 10 minutes - equally on Windows,
macOS and Linux.

---

## What you install (and what you don't)

You install **one single program**: `pixi`. Everything else - Python itself,
HyperSpy, all libraries - pixi then fetches automatically, in *exactly* the
versions pinned in `pixi.lock`.

That means:

- **You do not need Python installed.** No Anaconda, no Miniconda either.
- **Nothing on your system is changed.** Everything lands in the project folder
  under `.pixi/`. To uninstall, delete that folder.
- **Everyone gets identical versions.** No more "but it works on my machine".

---

## Step 1: install pixi

Find your operating system and run **one** command.

### Windows

Open PowerShell (Start menu -> type "PowerShell" -> Enter) and run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm -useb https://pixi.sh/install.ps1 | iex"
```

**Then close PowerShell and open it again** - otherwise Windows does not yet know
the `pixi` command.

### macOS

Open Terminal (Cmd+Space -> "Terminal" -> Enter) and run:

```bash
curl -fsSL https://pixi.sh/install.sh | sh
```

**Then close the terminal and open it again.**

### Linux

```bash
curl -fsSL https://pixi.sh/install.sh | sh
```

**Then close the terminal and open it again.**

### Did it work?

```bash
pixi --version
```

A version number means you can go to step 2. "Command not found" means: did you
really open a new terminal? If so, see [When something goes wrong](#when-something-goes-wrong).

---

## Step 2: get the project

**With Git** (recommended, so you can pull later corrections with `git pull`):

```bash
git clone https://github.com/marki155/STEMDataAnalysisWorkshop.git
cd STEMDataAnalysisWorkshop
```

**Without Git:** on the [GitHub page](https://github.com/marki155/STEMDataAnalysisWorkshop) click the green **Code** button ->
**Download ZIP** -> unpack it -> `cd` into the unpacked folder in a terminal.

---

## Step 3: get the measurement data

The measurement data is **not** in the repository. You download it once,
separately.

1. Download the data ZIP (43 MB, 152 MB unpacked): **https://gigamove.rwth-aachen.de/de/download/6f85be27210b21f30d00327ccc0acc37**
2. Unpack it.
3. Place the `nanopore` folder so that it ends up looking **exactly** like this:

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

> **The most common mistake is one folder level too many** - i.e.
> `data/measurements/nanopore/...` instead of `data/nanopore/...`. The notebooks
> usually still find the files, but step 4 will tell you exactly what it found where.

---

## Step 4: set up and check the environment

In the project folder:

```bash
pixi run check
```

The **first** call makes pixi download Python and every library - a few minutes
depending on your connection, and about 2 GB of disk. After that it is instant.

The command checks, in order:

1. are all packages present (with version numbers),
2. can `.dm3`/`.dm4` files be read,
3. does HyperSpy know the EELS and EDX signal types,
4. is the GOSH database present (42 MB, downloaded once - **do this before the
   workshop**, not while twenty people share the Wi-Fi),
5. is the measurement data in the right place.

At the end you get either `Everything ready.` or a list of what is still missing.

---

## Step 5: get going

```bash
pixi run lab
```

JupyterLab opens in your browser. Work through the notebooks in this order:

| Notebook | Contents |
| --- | --- |
| `00_setup_check.ipynb` | Checks installation, interactive plots and widgets |
| `01_EELS_modeling.ipynb` | EELS: align, background, edge model, fine structure |
| `02_EDX_modeling.ipynb` | EDX: line selection, model fit, background windows |
| `03_phase_mapping.ipynb` | Separating Si / SiO2 / WS2 / C+Pt by EELS and EDX *(template - needs your data)* |

**Always start the notebooks through `pixi run lab`.** If you start JupyterLab any
other way (a system-wide Jupyter, say), it uses the wrong Python and none of the
packages are there.

---

## When something goes wrong

<details>
<summary><b>"pixi: command not found" / "pixi is not recognized"</b></summary>

**Close and reopen** the terminal or PowerShell after installing. The installer adds
pixi to your search path, and that only takes effect in a new session.

If that does not help, call pixi by its full path:

- Windows: `%USERPROFILE%\.pixi\bin\pixi.exe --version`
- macOS/Linux: `~/.pixi/bin/pixi --version`

</details>

<details>
<summary><b>Plots stay blank, or you only get a grey box</b></summary>

The interactive Matplotlib backend (`ipympl`) is not working. In the top code cell
of the notebook, replace

```python
%matplotlib widget
```

with

```python
%matplotlib inline
```

and restart the kernel (menu **Kernel -> Restart Kernel and Run All Cells**). Plots
are then static, but identical in content.

</details>

<details>
<summary><b>Nothing renders with <code>%matplotlib widget</code>, but <code>inline</code> and <code>qt</code> work</b></summary>

If `%matplotlib inline` shows the plot and `%matplotlib qt` shows it in a separate
window, then matplotlib and HyperSpy are fine - the interactive **widget** is not
being rendered by JupyterLab. Work through this in order.

**1. Reload the browser page properly.** Ctrl+Shift+R (Cmd+Shift+R on macOS).
JupyterLab caches its extension bundle, and a stale cache is the most common cause.

**2. Check which extensions are actually loaded:**

```bash
pixi run extensions
```

`jupyter-matplotlib` and `@jupyter-widgets/jupyterlab-manager` must both be listed
as `enabled OK`, and they should come from the path inside `.pixi/envs/default`.
If a second directory is listed - your own Jupyter installation, on Windows
`%APPDATA%\jupyter\labextensions` - an older copy there can shadow the one pinned
in this project. `pixi run lab` sets `JUPYTER_PREFER_ENV_PATH=1` to prevent that,
so start JupyterLab that way and not with a system-wide `jupyter lab`.

**3. Is it only plots, or all widgets?** Run `00_setup_check.ipynb`. Section 2
tests an interactive plot, section 3 tests plain HyperSpy sliders.

- Sliders appear, plot does not -> the problem is `ipympl` alone.
- Neither appears -> the whole widget stack is not loading; see step 2.

**4. If it stays broken, use `%matplotlib inline`.** Replace the first code cell of
each notebook and restart the kernel. Everything in the workshop works; you lose
zoom and the click-a-pixel navigator, nothing else. `m.gui()` is off by default
anyway, and every interactive cell has a code variant next to it.

</details>

<details>
<summary><b>A plot does not appear at all</b></summary>

First find out whether the interactive backend is actually running. Put this in a
cell and run it:

```python
import matplotlib, matplotlib.pyplot as plt
print("backend    :", matplotlib.get_backend())
print("interactive:", plt.isinteractive())
print("figures    :", plt.get_fignums())
```

Expected inside a notebook: a backend whose name contains `widget`, `ipympl` or
`nbagg` (matplotlib reports it as `widget` or as `module://ipympl.backend_nbagg`,
depending on version), and `interactive: True`.

- **Backend is something else** (`qtagg`, `agg`, ...): `%matplotlib widget` did not
  take effect in this kernel. Restart the kernel and run the cells from the top.
- **`interactive` is False**: figures are built but never shown. `plt.ion()` fixes
  it for the session; a kernel restart fixes it properly.
- **Backend and interactive are right but `figures` lists the figure anyway**: the
  figure exists and the browser is not rendering it. Switch that notebook's first
  cell to `%matplotlib inline` and restart the kernel. Plots are then static, but
  they always appear.

An exception in an earlier cell can leave the kernel in a state where this
happens, so a restart is worth trying before anything else.

</details>

<details>
<summary><b>Only one plot appears where there should be two ("Figure 2" missing)</b></summary>

`signal.plot()` on a spectrum image normally opens **two** figures: a navigator -
the survey image you click on to pick a pixel - and the signal, the spectrum
itself. With `%matplotlib widget`, JupyterLab sometimes attaches only one of them
to the cell output, and the one that goes missing is usually "Figure 2", the
spectrum.

The notebooks avoid this by putting both panels into a single figure:

```python
hs.preferences.Plot.use_subfigure = True
```

That line sits in the import cell of notebooks 01, 02 and 03. If you write your
own notebook, set it there too.

Alternatives if you would rather keep two separate figures:

- `signal.plot(navigator="slider")` - one figure plus sliders, no navigator image
- `%matplotlib inline` - static plots, both always shown

</details>

<details>
<summary><b><code>m.gui()</code> shows only text instead of sliders</b></summary>

No problem: below every `m.gui()` cell there is a **Variant B** that does the same
thing in code. Use that one.

</details>

<details>
<summary><b>Windows: <code>ImportError: DLL load failed while importing ...</code></b></summary>

The package is installed; a compiled file next to it will not load. `pixi run check`
prints a diagnosis for this case, including which of the causes below applies to
your machine. In order of how often it is the answer:

**1. The project sits in OneDrive (or Dropbox, Google Drive, ...).** This is the
usual cause. With Files On-Demand a DLL is only a placeholder on disk until
something opens it, and Windows cannot load a placeholder as a library. Sync also
locks files while it works.

Move the whole project out of the synced folder - `C:\Users\<you>\Projects\STEMDataAnalysisWorkshop`
is fine - and run `pixi install` again. A 2 GB environment of compiled libraries
does not belong in cloud sync in the first place; it is rebuilt from `pixi.lock`
in minutes, so nothing is lost by not syncing it. Failing that, right-click the
`.pixi` folder and choose **Always keep on this device**, wait for the sync to
finish, and try again.

**2. The path is too long.** Windows refuses to load a library whose full path
exceeds 260 characters. `pixi run check` measures the longest one it can find and
tells you the number.

**3. Another Python on PATH supplies a conflicting DLL.** Check with `where python`
(PowerShell: `Get-Command python -All`). Anything other than this environment
should not come first. Always start through `pixi run`, never a system-wide
`python` or `conda`.

**4. Antivirus quarantined the file.** Check its log for the path in the error.

**5. The package unpacked incompletely.** `pixi clean` then `pixi install`.

</details>

<details>
<summary><b><code>ModuleNotFoundError: No module named 'hyperspy'</code></b></summary>

You did not start JupyterLab through `pixi run lab`. Close it and restart with that
command.

</details>

<details>
<summary><b><code>FileNotFoundError</code> when loading data</b></summary>

The error message tells you which path was expected and what is in `data/` instead.
Usually one folder level too many appeared while unpacking - compare against the
tree in step 3.

To see what is found:

```bash
pixi run python -c "import sys; sys.path.insert(0,'notebooks'); import workshop_data; workshop_data.status()"
```

</details>

<details>
<summary><b><code>TraitError: Broken link ... the source value changed while updating the target</code></b></summary>

This stops `multifit` part way through, usually with a line above it naming a
model parameter, e.g. `<Parameter intensity of O_K component>`.

**Cause:** an open `m.gui()` widget. It binds every model parameter to a slider.
While fitting, the optimiser writes each parameter thousands of times per second;
every value travels to the browser and comes back with float32 precision, so it
differs in about the eighth digit. The binding sees the source change while it is
updating the target and raises.

**Fix:** re-run the cell that creates the model -

```python
m = signal_binned.create_model(auto_background=False)
```

A fresh model has no widget attached, and the fit runs. You do not need to restart
the kernel.

**Avoiding it:** every `m.gui()` cell in notebooks 01 and 03 is switched off by
default (`SHOW_GUI = False`) for exactly this reason. If you turn one on, re-create
the model before you fit. Variant B, which prints the same information as text, has
no such problem.

</details>

<details>
<summary><b>The fit takes forever</b></summary>

`multifit` fits every pixel separately. Raise the `rebin` factor, e.g. from
`scale=[2, 2, 1]` to `[4, 4, 1]` - that quarters the number of pixels.

</details>

<details>
<summary><b>Start over from scratch</b></summary>

```bash
pixi clean
pixi install
```

Deletes the environment and rebuilds it from `pixi.lock`. Your notebooks and data
are untouched.

</details>

---

## For instructors

### Layout

```
pixi.toml            package list and the pixi tasks (maintained by hand)
pixi.lock            exact versions of every package, all 4 platforms - do NOT edit by hand
check_setup.py       setup check, also available as 'pixi run check'
notebooks/
  workshop_data.py   OS-independent data lookup with usable error messages
  phase_analysis.py  elemental maps -> phase map, and the X-ray line overlap check
  0*.ipynb           the workshop notebooks
data/                measurement data, excluded via .gitignore
```

### Tasks

```bash
pixi run check        # verify the installation and the data
pixi run lab          # start JupyterLab
pixi run extensions   # list the active JupyterLab extensions
```

`lab` and `extensions` set `JUPYTER_PREFER_ENV_PATH=1` so that JupyterLab loads the
extensions pinned in this project rather than any the user happens to have in their
own Jupyter directory. That matters for participants who already have a Jupyter
installation: an older `jupyter-matplotlib` there can shadow this one and interactive
plots then fail to render with no error message.

### Versions

Pinned in `pixi.lock` for `linux-64`, `win-64`, `osx-64` and `osx-arm64`:
HyperSpy 2.4.0, eXSpy 0.3.2, RosettaSciIO 0.14.0, NumPy 2.4.6, SciPy 1.18.0,
Matplotlib 3.10.9, Python 3.12.

**Matplotlib is deliberately pinned to `<3.11`.** HyperSpy 2.4.0 passes marker
colours in a form that Matplotlib 3.11 takes apart element by element; the call
`plot(background_windows=...)` in notebook 02 then dies with
`ValueError: Invalid RGBA argument`. Verified: it runs with 3.10.9. Only lift the
pin once a HyperSpy release has fixed this - and then actually run notebook 02
once end to end.

### Datasets

| Folder | Size | Used by | In the participant ZIP |
| --- | --- | --- | --- |
| `data/nanopore/` | 152 MB (ZIP: 43 MB) | notebooks 01 + 02 | yes |

That is the only dataset the workshop ships with. `03_your_own_data.ipynb` is a
template for measurements you add later.

### Notebook 03: phase mapping

Written for a sample with four phases - Si, SiO2, WS2 and a C+Pt cap - and mapped
twice, once by EELS and once by EDX, because the two methods fail in different
places. It is a **template**: the file paths are placeholders and it does not run
until you point it at a measurement. The bonus section at the end is the exception
and works with the workshop's own Si/SiO2 references.

Two facts drive its design, both checked against eXSpy 0.3.2 rather than assumed:

- **EELS cannot reach W or Pt below 1800 eV.** The lowest edges in the database are
  W-M5 = 1809 eV and Pt-M5 = 2122 eV, so in an 80-600 eV window `add_elements`
  silently drops both. EELS identifies WS2 through sulphur (S-L2,3 = 165 eV) and the
  cap through carbon (C-K = 284 eV).
- **EDX puts two free amplitudes 36 eV apart.** Si-Ka sits at 1.740 keV and W-Ma at
  1.776 keV. `add_lines()` correctly picks the clean L lines at 200 kV, but
  `create_model()` still builds the whole M family, and the M head is *not* tied to
  the L head - so both amplitudes float under one 130 eV-wide peak. The notebook
  detects this and ties the M family to the L family with a calibrated ratio.

### Colours for the elemental maps

Each element keeps its own hue, and lightness carries the amount. The hue belongs
to the element rather than to its place in a list, so adding an element does not
repaint the others. `ELEMENT_COLOURS` in `notebooks/phase_analysis.py` holds the
table; `plot_element_maps()` draws the panels.

The two sets the workshop draws side by side were checked as sets, not chosen by
eye - both clear the separation floors for normal and colour-deficient vision:

| Set | Colours | Worst pair (CVD / normal) |
| --- | --- | --- |
| Si, O, N | blue, orange, aqua | dE 9.2 / 24.0 |
| Si, O, S, C | blue, orange, aqua, violet | dE 9.2 / 16.3 |

Two limits, both reported at runtime rather than hidden:

- **N and S share the aqua.** Four checked hues cannot cover five elements. They
  never occur together in these notebooks; if they ever do, the function says so.
- **Past four maps at once** no assignment stays distinguishable - that is the
  colour space, not the table. Every panel carries the element name as its title,
  so identity never rests on colour alone.

Bright means more of the element, matching the usual convention for EELS and EDX
maps. Pass `bright_is_more=False` for a light-background version for print.

`phase_analysis.py` holds the parts that can be tested without a microscope: the
line-overlap detector and the classification. It carries its own self-test against
a layer stack whose answer is known:

```bash
pixi run python notebooks/phase_analysis.py
```

### Adding your own measurements

Drop the files into a subfolder of `data/`, then either point at them directly:

```python
signal = load_path("my_sample/EELS SI.dm4", signal_type="EELS")
```

or, once you use a file repeatedly, give it a name by extending `DATASETS` in
`notebooks/workshop_data.py`:

```python
DATASETS = {
    "my_sample_eels": "my_sample/EELS SI.dm4",
    ...
}
```

`load("my_sample_eels")` then works in every notebook and `pixi run check`
verifies the file is present. If the file is not part of the shared ZIP, add its
name to `OPTIONAL` in the same file so a missing file is a note, not an error.

Never write fixed paths into a notebook - they break on the next machine.

### Fitting reference spectra: use the linear solver

Where a model is a sum of fixed reference shapes with only their heights free, it
is **linear** in those heights. Do not fit it with the iterative optimiser:

```python
model.multifit(optimizer="nnls")     # not multifit(bounded=True)
```

`multifit` starts every pixel from the previous pixel's result. When several
references describe the same edge - as Si, Si3N4 and SiO2 all do - the sum is well
determined but the split between them is nearly degenerate, so the values drift
from pixel to pixel and eventually stick on the `bmin = 0` wall and stay there.
The map then shows a straight edge with everything beyond it exactly zero, which
looks like a real boundary.

Measured on the nanopore data, where the signal is symmetric top to bottom:

| Solver | Row means of the fitted weight, top -> bottom |
| --- | --- |
| iterative, `bounded=True` | 12475 12229 ... 7102 3407 **0 0 0 0 0 0** |
| `nnls` | 12475 12229 ... 6732 6790 7174 7759 8691 ... 12338 |

`nnls` solves each pixel exactly and independently, with non-negativity built in.

`check_fit_complete()` in `phase_analysis.py` catches both ways a fit fails while
looking finished: pixels the optimiser never reached, and parameters pinned to a
bound over more than a quarter of the map. A few percent of exact zeros is normal
with a non-negative solver and is not reported.

### Two silent failure modes worth knowing about

Both cost real time during development, because **neither raises an error**:

- `add_elements` accepts any element and then silently drops the ones whose edges
  lie outside the recorded energy window. The model quietly omits them and the
  results look plausible but mean nothing.
- `remove_background` accepts a `signal_range` that is not inside the data at all
  and returns something meaningless.

`workshop_data.check_elements(signal, elements)` and
`workshop_data.check_background_window(signal, window)` catch both. Notebook 03
runs them before every model; it is worth doing the same for your own analyses.

### Before distributing

Clear the notebook outputs before committing, otherwise the files grow to megabytes
and the diffs become useless:

```bash
pixi run jupyter nbconvert --clear-output --inplace notebooks/*.ipynb
```
