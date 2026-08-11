"""Shared chart style for all notebooks — one design language for every figure.

Palette and chrome follow a CVD-validated reference palette (adjacent-pair
color-vision-deficiency ΔE and surface-contrast checks): two categorical series
colors, an ordered blue↔red verdict scale with a neutral midpoint, and recessive
ink/grid tones. Figures render on a fixed light surface so the committed PNGs
look the same everywhere (including dark READMEs).

Usage in a notebook:

    from src import plotstyle as ps
    ps.apply()
    fig, ax = plt.subplots(figsize=(9, 6))
    ...
    ps.titles(ax, "Title", "Subtitle in secondary ink")
    ps.save(fig, "../output/figure.png")
"""

import matplotlib as mpl

# --- palette ---------------------------------------------------------------

SURFACE = "#fcfcfb"   # chart surface (figure + axes background)
INK = "#0b0b0b"       # primary text
INK_2 = "#52514e"     # secondary text (subtitles, axis labels, value labels)
MUTED = "#898781"     # muted labels
GRID = "#e1e0d9"      # hairline gridlines
BASELINE = "#c3c2b7"  # axis lines

BLUE = "#2a78d6"      # categorical slot 1
ORANGE = "#eb6834"    # categorical slot 2

# Ordered verdict scale (claims audit): diverging blue -> neutral -> red.
# Verdicts are ordered by how much of the claim survives, so the scale is
# polarity, not identity; always paired with direct text labels.
VERDICT_COLORS = {
    "holds (lemma)":      "#1c5cab",
    "holds (uniform)":    "#5598e7",
    "mixed methods only": "#898781",
    "one side only":      "#ec8987",
    "does not hold":      "#b52f2e",
}
NO_MATCH = "#f0efec"  # computed, no match (recedes toward the surface)

# --- rcParams --------------------------------------------------------------


def apply():
    """Set the shared matplotlib style. Call once per notebook, before plotting."""
    mpl.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": "DejaVu Sans",   # matplotlib's bundled font: identical renders everywhere
        "font.size": 11,
        "text.color": INK,
        "axes.labelcolor": INK_2,
        "axes.labelsize": 10.5,
        "axes.edgecolor": BASELINE,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": BASELINE,
        "ytick.color": BASELINE,
        "xtick.labelcolor": INK_2,
        "ytick.labelcolor": INK_2,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.frameon": False,
        "legend.fontsize": 10,
        "lines.linewidth": 2,
        "lines.solid_capstyle": "round",
    })


def titles(ax, title, subtitle=None):
    """Left-aligned title in primary ink; optional one-line subtitle in secondary ink."""
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", color=INK,
                 pad=26 if subtitle else 12)
    if subtitle:
        ax.annotate(subtitle, xy=(0, 1), xycoords="axes fraction",
                    xytext=(0, 8), textcoords="offset points",
                    fontsize=10, color=INK_2, va="bottom")


def save(fig, path):
    """Save with consistent resolution and margins, then release the figure."""
    fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.3)
    import matplotlib.pyplot as plt
    plt.close(fig)
