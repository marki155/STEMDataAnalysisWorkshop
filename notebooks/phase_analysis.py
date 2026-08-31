"""Turn elemental maps into a phase map, and warn about X-ray line overlaps.

Written for a sample containing four phases - Si, SiO2, WS2 and a C+Pt
protective cap - but nothing here is specific to those four. Both the scoring
rules and the palette are arguments.

Why this is a module and not notebook cells: the classification is ordinary
array code that can be tested without a microscope, and it is worth testing.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
# Categorical hues, fixed order, chosen for a map where every colour is on
# screen at once and regions touch each other. Validated for that case
# (all-pairs): worst colour-vision-deficient separation dE 9.2, worst
# normal-vision separation dE 16.3, both above the floors.
#
# The aqua sits below 3:1 contrast against a white figure, so the phase map is
# never colour-alone: it always ships with a legend, per-phase maps and the
# printed area fractions.
PHASE_COLOURS = {
    "Si": "#2a78d6",      # blue
    "SiO2": "#eb6834",    # orange
    "WS2": "#1baf7a",     # aqua
    "C+Pt": "#4a3aa7",    # violet
}
UNASSIGNED_COLOUR = "#b8b7b1"  # neutral grey - "no phase", not a category


# ---------------------------------------------------------------------------
# One colour per element, for the elemental maps
# ---------------------------------------------------------------------------
# An elemental map shows a magnitude, so each one gets a single-hue ramp running
# from the page colour up to that element's hue. The hue belongs to the element,
# not to its position in a list - adding an element must not repaint the others.
#
# The hues are taken in a fixed order and checked as a set, not picked by eye.
# The two combinations the workshop actually draws side by side both clear the
# separation floors for normal and colour-deficient vision:
#
#   Si, O, N     blue, orange, aqua            worst pair dE 9.2 (CVD) / 24.0 (normal)
#   Si, O, S, C  blue, orange, aqua, violet    worst pair dE 9.2 (CVD) / 16.3 (normal)
#
# Beyond four simultaneous maps no assignment clears those floors - that is a
# property of the colour space, not of this table. plot_element_maps() therefore
# says so out loud when you draw more than four, and every panel always carries
# the element name as its title, so identity never rests on colour alone.
#
# N and S share the aqua on purpose: they do not occur together in these
# notebooks, and four validated hues cannot cover five elements. If they ever do
# occur together, plot_element_maps() warns about it.
ELEMENT_COLOURS = {
    "Si": "#2a78d6",   # blue
    "O": "#eb6834",    # orange
    "N": "#1baf7a",    # aqua
    "S": "#1baf7a",    # aqua - see note above
    "C": "#4a3aa7",    # violet
    # Beyond the validated four:
    "W": "#eda100",    # yellow
    "Pt": "#008300",   # green
    "Ca": "#e87ba4",   # magenta
}
FALLBACK_COLOUR = "#52514e"   # dark neutral for anything not listed
SURFACE = "#fcfcfb"           # the page the maps sit on


def element_cmap(element, bright_is_more=True, surface=SURFACE):
    """A single-hue colormap for one element: one hue, lightness carries the value.

    Parameters
    ----------
    bright_is_more : bool
        True (default) runs dark -> hue -> pale, so a bright pixel means a lot of
        the element. That is the convention every EELS and EDX map follows, and
        it matches HyperSpy's own greyscale output, so a reader does not have to
        re-learn the direction.

        False runs the other way, pale page colour -> hue -> dark. Better when a
        figure is going into print on white paper, where a large black field is
        heavy and wasteful of ink.

    The generic chart rule is light-to-dark on a light page. Maps are the
    exception: they carry their own ground, and inverting a convention the reader
    already has costs more than it gains.
    """
    from matplotlib.colors import LinearSegmentedColormap, to_rgb

    hue = ELEMENT_COLOURS.get(element, FALLBACK_COLOUR)
    r, g, b = to_rgb(hue)
    dark = (r * 0.16, g * 0.16, b * 0.16)
    pale = (r + (1 - r) * 0.72, g + (1 - g) * 0.72, b + (1 - b) * 0.72)

    stops = [dark, hue, pale] if bright_is_more else [to_rgb(surface), hue, (r * 0.55, g * 0.55, b * 0.55)]
    return LinearSegmentedColormap.from_list(f"{element}_ramp", stops)


def plot_element_maps(maps, ncols=4, figsize_per_map=(3.6, 3.4), suptitle=None,
                      vmin=0, vmax=None, bright_is_more=True):
    """Draw one panel per element, each in its own colour.

    Parameters
    ----------
    maps : dict of str -> 2D array
        Element name -> map. Normalise them first if you want a shared scale.
    ncols : int
        Panels per row.
    vmax : float, optional
        Upper limit for every panel. Leave as None to let each panel scale
        itself, which shows weak elements but destroys comparability between
        panels - the colourbars then carry the actual numbers.
    bright_is_more : bool
        Passed to :func:`element_cmap`. True keeps the microscopy convention that
        a bright pixel means more of the element.
    """
    import matplotlib.pyplot as plt
    import numpy as np

    if not maps:
        print("nothing to plot")
        return None

    names = list(maps)

    # Two things worth saying out loud rather than letting them pass unnoticed.
    used = {}
    for name in names:
        used.setdefault(ELEMENT_COLOURS.get(name, FALLBACK_COLOUR), []).append(name)
    clashes = [group for group in used.values() if len(group) > 1]
    if clashes:
        print(f"[WARNING] These elements share a colour in this figure: {clashes}.")
        print("          Edit ELEMENT_COLOURS in phase_analysis.py to separate them.")
    if len(names) > 4:
        print(f"[NOTE] {len(names)} maps at once. Only four hues are checked to stay")
        print("       apart for colour-deficient vision; past that, read the titles.")

    nrows = int(np.ceil(len(names) / ncols))
    ncols_used = min(ncols, len(names))
    fig, axes = plt.subplots(
        nrows, ncols_used,
        figsize=(figsize_per_map[0] * ncols_used, figsize_per_map[1] * nrows),
        squeeze=False,
    )
    for ax, name in zip(axes.ravel(), names):
        data = np.asarray(maps[name], float)
        image = ax.imshow(
            data, cmap=element_cmap(name, bright_is_more=bright_is_more), vmin=vmin,
            vmax=vmax if vmax is not None else np.nanmax(data),
            interpolation="nearest",
        )
        ax.set_title(name, fontsize=11)
        ax.set_xticks([]); ax.set_yticks([])
        fig.colorbar(image, ax=ax, shrink=0.82)
    for ax in axes.ravel()[len(names):]:
        ax.axis("off")
    if suptitle:
        fig.suptitle(suptitle)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# EDX: which lines sit on top of each other
# ---------------------------------------------------------------------------
def check_xray_lines(elements, beam_energy_kv=200.0, resolution_ev=130.0,
                     min_weight=0.05, verbose=True):
    """List the X-ray lines of `elements` and flag pairs a detector cannot separate.

    A silicon drift detector has a resolution of roughly 130 eV (FWHM at Mn-Ka).
    Two lines closer than that are one peak, and fitting them as two is guesswork.
    This matters a lot for the Si/WS2 combination: Si-Ka at 1.740 keV and W-Ma at
    1.776 keV are 36 eV apart.

    Parameters
    ----------
    elements : list of str
    beam_energy_kv : float
        Lines above this cannot be excited, so they are ignored.
    resolution_ev : float
        Detector resolution. Pairs closer than this are reported as overlapping.
    min_weight : float
        Ignore lines weaker than this relative weight.

    Returns
    -------
    dict
        ``{"lines": [(element, line, keV, weight), ...],
           "overlaps": [(element_a, line_a, element_b, line_b, separation_eV), ...]}``
    """
    from exspy.material import elements as element_db

    lines = []
    for element in elements:
        try:
            table = element_db[element]["Atomic_properties"]["Xray_lines"].as_dictionary()
        except (KeyError, AttributeError):
            if verbose:
                print(f"  no X-ray line data for {element!r}")
            continue
        for line, info in table.items():
            energy, weight = float(info["energy (keV)"]), float(info["weight"])
            if weight >= min_weight and energy < beam_energy_kv:
                lines.append((element, line, energy, weight))
    lines.sort(key=lambda row: row[2])

    overlaps = []
    for i in range(len(lines) - 1):
        for j in range(i + 1, len(lines)):
            separation = (lines[j][2] - lines[i][2]) * 1000.0
            if separation > resolution_ev:
                break  # sorted by energy, so everything further is further away
            if lines[i][0] != lines[j][0]:  # same element overlapping itself is fine
                overlaps.append((lines[i][0], lines[i][1],
                                 lines[j][0], lines[j][1], separation))

    if verbose:
        print(f"X-ray lines below {beam_energy_kv:.0f} kV with weight >= {min_weight}:\n")
        for element, line, energy, weight in lines:
            print(f"  {element:3s} {line:6s} {energy:7.3f} keV   weight {weight:.2f}")
        print(f"\nDetector resolution assumed: {resolution_ev:.0f} eV\n")
        if overlaps:
            print("Pairs the detector cannot separate:")
            for a, la, b, lb, sep in overlaps:
                print(f"  [OVERLAP] {a}-{la} and {b}-{lb} are {sep:.0f} eV apart")
            print(
                "\nQuantifying either line of such a pair without the other in the\n"
                "model gives a wrong answer. Use a line of the same element that is\n"
                "free of overlap instead - for heavy elements usually the L series."
            )
        else:
            print("No overlapping pairs at this resolution.")

    return {"lines": lines, "overlaps": overlaps}


# ---------------------------------------------------------------------------
# Elemental maps -> phase map
# ---------------------------------------------------------------------------
def normalise(array, percentile=99.0):
    """Scale a map to roughly 0..1 using a percentile, so hot pixels do not set the scale.

    Values are clipped at 0 below and at 1 above, and an all-zero map stays
    all-zero instead of turning into NaN.
    """
    data = np.asarray(array, dtype=float)
    data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
    top = np.percentile(data, percentile)
    if not np.isfinite(top) or top <= 0:
        return np.zeros_like(data)
    return np.clip(data / top, 0.0, 1.0)


def phase_scores(maps):
    """Score every pixel for the four phases from normalised elemental maps.

    Expects ``maps`` to hold normalised maps under the keys "Si", "O", "S", "C".
    The rules are deliberately simple and written out, so you can argue with them:

    * ``WS2``  - sulphur is present. Nothing else in this sample contains S.
    * ``C+Pt`` - carbon is present. Nothing else in this sample contains C.
    * ``SiO2`` - silicon *and* oxygen. ``min`` demands both, not just one.
    * ``Si``   - silicon *without* oxygen. The ``(1 - O)`` factor suppresses
      the pixel as soon as oxygen appears.

    Returns
    -------
    dict of str -> 2D array
    """
    missing = {"Si", "O", "S", "C"} - set(maps)
    if missing:
        raise KeyError(
            f"phase_scores needs maps for Si, O, S and C - missing: {sorted(missing)}.\n"
            "Pass a dict like {'Si': si_map, 'O': o_map, 'S': s_map, 'C': c_map}."
        )
    si, o, s, c = (np.asarray(maps[k], float) for k in ("Si", "O", "S", "C"))
    return {
        "Si": si * (1.0 - o),
        "SiO2": np.minimum(si, o),
        "WS2": s,
        "C+Pt": c,
    }


def classify(scores, threshold=0.15):
    """Assign each pixel to its highest-scoring phase.

    Pixels whose best score stays below ``threshold`` are left unassigned - that
    is what vacuum, the sample edge and plain noise should end up as. Raising the
    threshold shrinks the phases and grows the unassigned region.

    Returns
    -------
    labels : 2D int array
        0 = unassigned, 1..n = index into ``names``.
    names : list of str
        Phase names, in the order they are numbered.
    """
    names = list(scores)
    stack = np.stack([np.asarray(scores[n], float) for n in names])
    best = stack.argmax(axis=0)
    strength = stack.max(axis=0)
    labels = np.where(strength >= threshold, best + 1, 0)
    return labels.astype(int), names


def phase_fractions(labels, names):
    """Area fraction per phase, as a printable table.

    This is the table view that has to accompany the map: colour alone must not
    be the only way to read the result.
    """
    total = labels.size
    rows = [("unassigned", int((labels == 0).sum()))]
    rows += [(name, int((labels == i + 1).sum())) for i, name in enumerate(names)]
    print(f"{'phase':14s} {'pixels':>8s} {'area':>8s}")
    print("-" * 32)
    for name, count in rows:
        print(f"{name:14s} {count:8d} {100 * count / total:7.1f}%")
    return {name: count / total for name, count in rows}


def plot_phase_map(labels, names, ax=None, colours=None, title="Phase map"):
    """Draw the phase map with a legend naming every phase.

    The legend is not optional. One of the hues is light against white, and a
    map without a key is unreadable for anyone who cannot separate the colours.
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch

    colours = colours or PHASE_COLOURS
    ordered = [UNASSIGNED_COLOUR] + [colours[n] for n in names]
    cmap = ListedColormap(ordered)

    if ax is None:
        _fig, ax = plt.subplots(figsize=(6, 5))
    ax.imshow(labels, cmap=cmap, vmin=0, vmax=len(ordered) - 1, interpolation="nearest")
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.legend(
        handles=[Patch(facecolor=UNASSIGNED_COLOUR, edgecolor="#5a5a57", label="unassigned")]
        + [Patch(facecolor=colours[n], edgecolor="#5a5a57", label=n) for n in names],
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=False,
    )
    return ax


# ---------------------------------------------------------------------------
# Self-test - run with:  pixi run python notebooks/phase_analysis.py
# ---------------------------------------------------------------------------
def _self_test():
    """Check the classification against a layer stack whose answer is known."""
    ny, nx = 80, 60
    truth = np.zeros((ny, nx), int)
    truth[55:80] = 1   # Si
    truth[45:55] = 2   # SiO2
    truth[30:45] = 3   # WS2
    truth[10:30] = 4   # C+Pt
    #  rows 0..10 stay vacuum

    rng = np.random.default_rng(0)
    def band(mask, noise=0.06):
        return np.clip(mask * 1.0 + rng.normal(0, noise, (ny, nx)), 0, None)

    maps = {
        "Si": band((truth == 1) | (truth == 2)),   # silicon is in Si *and* SiO2
        "O": band(truth == 2),
        "S": band(truth == 3),
        "C": band(truth == 4),
    }
    maps = {k: normalise(v) for k, v in maps.items()}
    labels, names = classify(phase_scores(maps), threshold=0.15)

    index = {"Si": 1, "SiO2": 2, "WS2": 3, "C+Pt": 4}
    predicted = np.zeros_like(labels)
    for i, name in enumerate(names):
        predicted[labels == i + 1] = index[name]

    accuracy = (predicted == truth).mean()
    print(f"classification against known truth: {100 * accuracy:.1f}% correct")
    for i, name in [(0, "vacuum"), (1, "Si"), (2, "SiO2"), (3, "WS2"), (4, "C+Pt")]:
        region = truth == i
        print(f"  {name:8s} {100 * (predicted[region] == i).mean():5.1f}%")
    assert accuracy > 0.95, f"classification is broken: {accuracy:.3f}"

    # A map of only zeros, or only NaN, must not turn into NaN.
    assert not np.isnan(normalise(np.zeros((4, 4)))).any()
    assert not np.isnan(normalise(np.full((4, 4), np.nan))).any()
    print("edge cases (all-zero map, all-NaN map): ok")

    try:
        phase_scores({"Si": np.zeros((4, 4))})
    except KeyError:
        print("missing maps raise a clear error: ok")
    else:  # pragma: no cover
        raise AssertionError("phase_scores accepted an incomplete set of maps")

    print("\nself-test passed")


if __name__ == "__main__":
    _self_test()
