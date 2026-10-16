"""House chart style — editorial data journalism for papers and the web.

Read `STYLE_GUIDE.md` next to this file first: it is the spec (palettes,
roles, chart recipes, paper vs web). This module is the mechanism:

- `set_style(bg="white"|"cream", medium="paper"|"web")` — fonts, chrome,
  sizes. White for journals, cream (the European Correspondent canvas) for
  the personal website / social posts only.
- palettes as data: `CATEGORICAL`, `SEQUENTIAL`, `DIVERGING`, `cmap()`,
  validated by `python -m modules.dataviz_style.palette_check`.
- helpers that make a chart look edited rather than exported: direct
  labels, context lines, gridline labels, elbow callouts, event lines,
  highlight spans, coloured words, stepped legends, panel titles/letters.
- a few chart shapes the defaults get wrong: lollipop, dot strip
  (dumbbell), waffle, highlight bars.
- `compose_poster()` — the only place a title is baked into the image.

Every plotting function in a project should take data (+ optional `ax`),
return the Figure, and never call `ax.set_title()` — captions live in the
paper / the page.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Literal, Sequence

import matplotlib.colors as mcolors
import matplotlib.font_manager as fm
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import numpy as np
from matplotlib.patches import Rectangle

Bg = Literal["white", "cream"]
Medium = Literal["paper", "web"]

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------
FONT_SANS = "IBM Plex Sans"    # tick labels, axis titles: the data's "small print"
FONT_SERIF = "IBM Plex Serif"  # direct labels, callouts, panel titles, poster headline
FONT_MONO = "IBM Plex Mono"    # code-like metadata only (run ids, hashes)

FONTS_DIR = Path(__file__).resolve().parent / "fonts"

# ---------------------------------------------------------------------------
# Surfaces — every neutral is defined per background, never shared.
# ---------------------------------------------------------------------------
SURFACES: dict[str, dict[str, str]] = {
    "white": {                 # journals, theses, slides, PDFs — the default
        "bg": "#ffffff",
        "ink": "#2b2522",      # warm near-black, text only (never a series)
        "muted": "#7a726c",    # tick labels, secondary text (4.7:1)
        "grid": "#ece8e2",
        "rule": "#d6d0c8",     # reference lines: chance, zero, average
        "context": "#c4bdb4",  # context series (always direct-labelled)
        "context_text": "#8a827a",
        "land": "#e4e1dc",     # maps: land not carrying data
        "panel": "#f7f4f0",    # shaded group panel behind a block of rows
    },
    "cream": {                 # personal website / social only — never a journal
        "bg": "#f3eeeb",       # European Correspondent canvas
        "ink": "#1f1a17",
        "muted": "#6e665f",
        "grid": "#e2dbd5",
        "rule": "#cfc7bf",
        "context": "#bfb7ae",
        "context_text": "#857c74",
        "land": "#d4d4d4",     # EC map land gray
        "panel": "#ebe4df",
    },
}

# ---------------------------------------------------------------------------
# Palettes — colors are roles, assigned by identity, never by plotting order.
# ---------------------------------------------------------------------------
WINE, GOLD, GREEN, VIOLET = "#a61b57", "#b07d00", "#1ea381", "#a35ec1"
ROSE, APRICOT, JADE, PLUM = "#af535f", "#dfa044", "#29a987", "#723c7e"
YELLOW, MINT, MAUVE = "#f4c54d", "#69c2a4", "#a885a6"   # HolidayCalc fills
YELLOW_TEXT, MINT_TEXT = "#b07d00", "#097d5a"           # their text twins (>= 3:1)

CATEGORICAL: dict[str, dict] = {
    "house": {
        "colors": [WINE, GOLD, GREEN, VIOLET],
        "use": "default for lines/dots, papers and web; strongest separation",
    },
    "editorial": {
        "colors": [ROSE, APRICOT, JADE, PLUM],
        "use": "softer EC register; web essays, also fine in papers",
        "band": (0.43, 0.78),
    },
    "pastel": {
        "colors": [YELLOW, MINT, MAUVE, WINE],
        "use": "HolidayCalc fills: bars, areas, calendar cells; labels in text twins",
        "band": (0.43, 0.86),
        "chroma": 0.05,
    },
}

SEQUENTIAL: dict[str, list[str]] = {
    # light -> dark; first step is the "almost nothing" tint
    "wine":  ["#fbe6ea", "#f0b3c0", "#d9708a", "#a61b57", "#6b0f39", "#3d0a22"],
    "gold":  ["#fdf1cc", "#f9db93", "#f4c54d", "#ca9e35", "#a2791d", "#7a5500"],
    "sage":  ["#e6e8d4", "#c3cca6", "#97ad84", "#6c8f6b", "#4e7866", "#2f5446"],
    "ember": ["#fbebb8", "#f2a86e", "#d9574f", "#9c185a", "#4c1d4b", "#261535"],  # EC "Thunderbolt"
    "warm":  ["#f2b880", "#e48a6e", "#b8566a", "#7d4a6b"],  # EC ordinal groups (age bands)
}

DIVERGING: dict[str, list[str]] = {
    # negative arm, light neutral midpoint, positive arm (odd length).
    # Purple <-> gold is the only blue-free pair that survives CVD: every
    # red/wine <-> green/sage/teal/gray candidate collapses for deutans at
    # equal lightness (see STYLE_GUIDE.md §3.4).
    "violet_gold":  ["#4a1f6b", "#7d3fa3", "#b48ad1", "#dccbe9", "#eeeae4",
                     "#f2d088", "#e6b43c", "#b07d00", "#704f00"],
    "plum_apricot": ["#3f1f4a", "#723c7e", "#a77bb0", "#d6c3da", "#eeeae4",
                     "#f6d6ad", "#eba862", "#bd7a2a", "#7a4a12"],
}

SOLID, DASHED, DOTTED, DASHDOT = "-", (0, (5, 2)), (0, (1, 1.6)), (0, (6, 2, 1, 2))
LINESTYLES = [SOLID, DASHED, DOTTED, DASHDOT]

# ---------------------------------------------------------------------------
# Media — sizes at FINAL print size (paper) or at 100 % CSS width (web).
# ---------------------------------------------------------------------------
MEDIA: dict[str, dict[str, float]] = {
    "paper": {"font": 8.0, "tick": 7.2, "label": 8.0, "direct": 7.6, "panel": 8.6,
              "lw": 1.5, "lw_context": 1.0, "marker": 3.0, "grid_lw": 0.6, "axis_lw": 0.7},
    "web":   {"font": 9.5, "tick": 8.5, "label": 9.5, "direct": 8.6, "panel": 10.0,
              "lw": 2.0, "lw_context": 1.3, "marker": 3.4, "grid_lw": 0.8, "axis_lw": 0.9},
}

# Journal column widths in inches (Elsevier / Springer / OUP are within a few mm).
WIDTHS = {"single": 3.5, "onehalf": 5.5, "double": 7.2, "web": 7.0, "web_wide": 9.0}

BAR_WIDTH = 0.5
LOLLIPOP_LW = 2.5
LOLLIPOP_MS = 7
ROW_HEIGHT = 0.42
FIGSIZE_MIN_H = 2.0
DPI_SAVE = 300

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
_fonts_registered = False
_state: dict[str, str] = {"bg": "white", "medium": "paper"}


def _register_fonts() -> None:
    """Register the bundled IBM Plex files; otherwise matplotlib silently falls back to DejaVu."""
    global _fonts_registered
    if _fonts_registered:
        return
    for path in FONTS_DIR.glob("*.ttf"):
        fm.fontManager.addfont(str(path))
    _fonts_registered = True


def theme() -> dict[str, str]:
    """Neutral tokens of the current background (ink, muted, grid, context, ...)."""
    return SURFACES[_state["bg"]]


def media() -> dict[str, float]:
    """Size tokens of the current medium."""
    return MEDIA[_state["medium"]]


def set_style(bg: Bg | None = None, medium: Medium | None = None) -> None:
    """Apply the house style. Call once per notebook; chart functions call it again with no args.

    Both choices are sticky: `None` keeps whatever was set last (initially
    white + paper), so a chart function calling `set_style()` for itself
    never undoes the notebook's (or `compose_poster`'s) decision.
    """
    if bg is not None:
        _state["bg"] = bg
    if medium is not None:
        _state["medium"] = medium
    _register_fonts()
    t, m = theme(), media()
    plt.rcParams.update({
        "font.family": FONT_SANS, "font.size": m["font"],
        "text.color": t["ink"], "axes.labelcolor": t["ink"], "axes.titlecolor": t["ink"],
        "xtick.color": t["muted"], "ytick.color": t["muted"],
        "xtick.labelcolor": t["muted"], "ytick.labelcolor": t["muted"],
        "xtick.labelsize": m["tick"], "ytick.labelsize": m["tick"], "axes.labelsize": m["label"],
        "axes.facecolor": t["bg"], "figure.facecolor": t["bg"], "savefig.facecolor": t["bg"],
        "axes.edgecolor": t["ink"], "axes.linewidth": m["axis_lw"],
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.grid.axis": "y", "axes.axisbelow": True,
        "grid.color": t["grid"], "grid.linewidth": m["grid_lw"],
        "axes.prop_cycle": plt.cycler(color=CATEGORICAL["house"]["colors"]),
        "lines.linewidth": m["lw"], "lines.solid_capstyle": "round", "lines.markersize": m["marker"],
        "patch.linewidth": 0,
        "legend.frameon": False, "legend.fontsize": m["tick"], "legend.labelcolor": t["ink"],
        "xtick.major.size": 3, "ytick.major.size": 0, "xtick.major.width": m["axis_lw"],
        "figure.dpi": 110, "savefig.dpi": DPI_SAVE, "savefig.bbox": "tight", "savefig.pad_inches": 0.04,
        "svg.fonttype": "none", "pdf.fonttype": 42, "ps.fonttype": 42,   # editable, embeddable text
        "axes.unicode_minus": True,
    })


def figsize(width: str | float = "single", aspect: float = 0.62) -> tuple[float, float]:
    """(w, h) in inches for a journal column ("single", "onehalf", "double") or the web."""
    w = WIDTHS[width] if isinstance(width, str) else float(width)
    return (w, w * aspect)


def palette(name: str = "house", n: int | None = None) -> list[str]:
    """Colors of a named palette; for ramps, `n` evenly spread steps."""
    if name in CATEGORICAL:
        cols = CATEGORICAL[name]["colors"]
        if n is not None and n > len(cols):
            raise ValueError(f"'{name}' has {len(cols)} slots; use small multiples or highlight + context")
        return cols[:n] if n else list(cols)
    ramp = SEQUENTIAL.get(name) or DIVERGING[name]
    if n is None:
        return list(ramp)
    c = cmap(name)
    return [mcolors.to_hex(c(v)) for v in np.linspace(0, 1, n)]


def cmap(name: str, steps: int | None = None) -> mcolors.Colormap:
    """Continuous (or `steps`-class stepped) colormap from a sequential/diverging ramp."""
    ramp = SEQUENTIAL.get(name) or DIVERGING[name]
    c = mcolors.LinearSegmentedColormap.from_list(name, ramp)
    if steps:
        return mcolors.ListedColormap([c(v) for v in np.linspace(0, 1, steps)], name=f"{name}_{steps}")
    return c


def save_fig(fig: plt.Figure, path: Path | str, formats: Sequence[str] | str | None = None) -> list[Path]:
    """Save next to `path` (extension ignored) in every format of the medium.

    paper -> pdf (submission, fonts embedded) + svg + png (preview / Word);
    web -> svg. Pass `formats="png"` for posters or charts with 1000s of points.
    """
    if formats is None:
        formats = ("pdf", "svg", "png") if _state["medium"] == "paper" else ("svg",)
    if isinstance(formats, str):
        formats = (formats,)
    path = Path(path)
    stem = path.with_suffix("") if path.suffix in {".png", ".svg", ".pdf"} else path
    stem.parent.mkdir(parents=True, exist_ok=True)
    out = []
    for fmt in formats:
        p = stem.with_name(f"{stem.name}.{fmt}")
        fig.savefig(p, facecolor=fig.get_facecolor())  # a poster keeps its cream after set_style() reset
        out.append(p)
    return out


# ---------------------------------------------------------------------------
# Labels, rules and annotations
# ---------------------------------------------------------------------------
def _offset(fig: plt.Figure, dx_pt: float = 0, dy_pt: float = 0) -> mtransforms.Transform:
    return mtransforms.ScaledTranslation(dx_pt / 72, dy_pt / 72, fig.dpi_scale_trans)


def label_color(color: str) -> str:
    """Text color for a label of a series drawn in `color` (light fills get their darker twin)."""
    t = theme()
    twins = {t["context"]: t["context_text"], YELLOW: YELLOW_TEXT, MINT: MINT_TEXT}
    return twins.get(color, color)


def direct_labels(ax: plt.Axes, items: Sequence[tuple[float, float, str, str]], dx: float = 5,
                  min_gap: float = 0.055, dots: bool = False, weight: str = "normal") -> None:
    """Serif labels right of line ends, nudged apart vertically; replaces the legend.

    `items` = [(x_end, y_end, text, color)]. `min_gap` is in axes fraction.
    `dots=True` adds the EC end dot. Call after the y-limits are final.
    """
    if not items:
        return
    y0, y1 = ax.get_ylim()
    span = y1 - y0
    items = sorted(items, key=lambda t: t[1])
    placed: list[float] = []
    for _, y, _, _ in items:
        placed.append(y if not placed else max(y, placed[-1] + min_gap * span))
    overflow = placed[-1] - (y1 - 0.01 * span)
    if overflow > 0:
        placed = [p - overflow for p in placed]
    tr = ax.transData + _offset(ax.figure, dx + (3 if dots else 0))
    for (x, y, text, color), yy in zip(items, placed):
        if dots:
            ax.plot([x], [y], "o", color=color, markersize=media()["marker"] + 2.2, markeredgewidth=0,
                    zorder=6, clip_on=False)
        ax.text(x, yy, text, transform=tr, fontfamily=FONT_SERIF, fontsize=media()["direct"],
                color=label_color(color), va="center", ha="left", fontweight=weight, clip_on=False)


def context_lines(ax: plt.Axes, x, Y: dict[str, Sequence[float]] | np.ndarray, label: bool = False) -> None:
    """Many thin light lines that set the scene behind the 1-3 highlighted series."""
    t, m = theme(), media()
    rows = Y.items() if isinstance(Y, dict) else enumerate(np.atleast_2d(Y))
    ends = []
    for name, y in rows:
        ax.plot(x, y, color=t["context"], lw=m["lw_context"] * 0.7, zorder=1, solid_capstyle="butt")
        ends.append((np.asarray(x)[-1], np.asarray(y)[-1], str(name), t["context"]))
    if label:
        direct_labels(ax, ends)


def ref_line(ax: plt.Axes, y: float | None = None, x: float | None = None, label: str | None = None,
             strong: bool = False) -> None:
    """Reference rule: chance level, average (dotted rule gray) or a zero baseline (`strong`, solid ink)."""
    t = theme()
    kw = dict(color=t["ink"] if strong else t["rule"], lw=0.9 if strong else 1.0,
              ls="-" if strong else (0, (2, 2)), zorder=1)
    if y is not None:
        ax.axhline(y, **kw)
        if label:
            ax.text(1.0, y, label, transform=ax.get_yaxis_transform(), ha="right", va="bottom",
                    fontfamily=FONT_SERIF, fontsize=media()["direct"] * 0.95, color=t["muted"])
    if x is not None:
        ax.axvline(x, **kw)


def panel_title(ax: plt.Axes, text: str, x: float = 0.0, y: float = 1.03, va: str = "bottom",
                inside: bool = False) -> None:
    """Serif semibold title of a small-multiple panel (allowed: it names the panel, not the figure)."""
    if inside:
        x, y, va = 0.03, 0.97, "top"
    ax.text(x, y, text, transform=ax.transAxes, fontfamily=FONT_SERIF, fontsize=media()["panel"],
            color=theme()["ink"], fontweight="bold", va=va, ha="left")


def panel_letter(ax: plt.Axes, letter: str, x: float = -0.12, y: float = 1.03) -> None:
    """Bold a, b, c panel letters for multi-panel paper figures referenced in the text."""
    ax.text(x, y, letter, transform=ax.transAxes, fontfamily=FONT_SANS, fontsize=media()["panel"],
            fontweight="semibold", color=theme()["ink"], va="bottom", ha="left")


def gridline_labels(ax: plt.Axes, ticks: Sequence[float] | None = None,
                    fmt: Callable[[float], str] = "{:g}".format, unit: str | None = None, dy: float = 1.5) -> None:
    """EC value axis: labels sit ON the gridlines at the left edge, unit appended to the top one.

    Removes the y spine and tick labels; call after the y-limits are final.
    """
    t = theme()
    lo, hi = ax.get_ylim()
    ticks = [v for v in (ticks if ticks is not None else ax.get_yticks()) if lo <= v <= hi]
    ax.set_yticks(ticks)
    ax.set_yticklabels([])
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    tr = ax.get_yaxis_transform() + _offset(ax.figure, 0, dy)
    for v in ticks:
        text = fmt(v).replace("-", "−") + (f" {unit}" if unit and v == max(ticks) else "")
        ax.text(0, v, text, transform=tr, ha="left", va="bottom", fontsize=media()["tick"],
                color=t["muted"], fontfamily=FONT_SANS, zorder=5,
                path_effects=[pe.withStroke(linewidth=2.5, foreground=t["bg"])])


def unit_label(ax: plt.Axes, text: str, x: float = 0.0, y: float = 1.03) -> None:
    """Horizontal axis unit above the value axis instead of a rotated y label (EC)."""
    ax.set_ylabel("")
    ax.text(x, y, text, transform=ax.transAxes, ha="left", va="bottom", fontfamily=FONT_SERIF,
            fontsize=media()["direct"], color=theme()["ink"], fontweight="bold", linespacing=1.0)


def axis_break(ax: plt.Axes, size: float = 7) -> None:
    """Zigzag at the bottom of the value axis: 'this axis does not start at zero'."""
    s = size / 72  # inches
    tr = ax.figure.dpi_scale_trans + mtransforms.ScaledTranslation(0, 0, ax.transAxes)
    xs = np.array([0, -0.5, 0.5, -0.5, 0.5, 0]) * s * 0.6
    ys = np.linspace(0.25, 1.25, 6) * s
    ax.plot(xs, ys, transform=tr, color=theme()["ink"], lw=0.8, clip_on=False, zorder=6)


def callout(ax: plt.Axes, xy: tuple[float, float], xytext: tuple[float, float], text: str | None = None,
            title: str | None = None, ha: str = "left", elbow: bool = True, italic: bool = False,
            textcoords: str = "data", color: str | None = None) -> None:
    """EC annotation: thin ink leader with a right-angle elbow, optional bold title above the text.

    `xy` = the data point, `xytext` = the anchor of the text block (its top
    edge for `text`, bottom edge for `title`), in `textcoords`.
    """
    t, m = theme(), media()
    color = color or t["ink"]
    halo = [pe.withStroke(linewidth=3, foreground=t["bg"])]
    conn = "angle,angleA=0,angleB=90,rad=0" if elbow else "arc3"
    ax.annotate(text or "", xy=xy, xytext=xytext, textcoords=textcoords, ha=ha, va="top",
                fontfamily=FONT_SERIF, fontsize=m["direct"], color=color, style="italic" if italic else "normal",
                linespacing=1.0, zorder=7, annotation_clip=False, path_effects=halo,
                arrowprops=dict(arrowstyle="-", color=t["ink"], lw=0.7, shrinkA=2, shrinkB=3,
                                connectionstyle=conn))
    if title:
        base = {"data": ax.transData, "axes fraction": ax.transAxes}[textcoords]
        ax.text(*xytext, title, transform=base + _offset(ax.figure, 0, 2), ha=ha, va="bottom",
                fontfamily=FONT_SERIF, fontsize=m["direct"], fontweight="bold", color=color, zorder=7,
                path_effects=halo)


def event_line(ax: plt.Axes, x: float, title: str, text: str | None = None, top: float = 1.0,
               ha: str = "center") -> None:
    """Vertical ink rule from the axis to a bold title + italic note above it (EC 'Crude prices')."""
    t, m = theme(), media()
    ax.plot([x, x], [0, top], transform=ax.get_xaxis_transform(), color=t["ink"], lw=0.8, zorder=4, clip_on=False)
    dy = 3
    if text:
        ax.text(x, top, text, transform=ax.get_xaxis_transform() + _offset(ax.figure, 0, dy), ha=ha, va="bottom",
                fontfamily=FONT_SERIF, style="italic", fontsize=m["direct"] * 0.95, color=t["ink"], linespacing=1.0)
        dy += (text.count("\n") + 1) * m["direct"] * 1.2 + 1
    ax.text(x, top, title, transform=ax.get_xaxis_transform() + _offset(ax.figure, 0, dy), ha=ha, va="bottom",
            fontfamily=FONT_SERIF, fontweight="bold", fontsize=m["direct"], color=t["ink"], linespacing=1.0)


def highlight_span(ax: plt.Axes, x0: float, x1: float, color: str = APRICOT, alpha: float = 0.85,
                   gradient: bool = True) -> None:
    """Shade a period (vertical band); with `gradient` it fades out towards the top (EC 'Out-of-office')."""
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    tr = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    if gradient:
        rgba = np.zeros((256, 1, 4))
        rgba[..., :3] = mcolors.to_rgb(color)
        rgba[..., 3] = (np.linspace(0, 1, 256) ** 1.3 * alpha)[:, None]
        ax.imshow(rgba, extent=[x0, x1, 0, 1], transform=tr, aspect="auto", origin="upper",
                  zorder=0, interpolation="bilinear")
    else:
        ax.add_patch(Rectangle((x0, 0), x1 - x0, 1, transform=tr, color=color, alpha=alpha * 0.25,
                               lw=0, zorder=0))
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)


def rich_text(ax: plt.Axes, x: float, y: float, segments: Sequence[tuple[str, dict]],
              transform: mtransforms.Transform | None = None, **common) -> None:
    """One line of text whose words differ in color/weight — the EC 'legend inside the sentence'.

    `segments` = [("Real meat", {"color": ROSE, "fontweight": "bold"}), (" and ", {}), ...].
    """
    kw = dict(fontfamily=FONT_SERIF, fontsize=media()["label"], color=theme()["ink"])
    kw.update(common)
    first, *rest = segments
    prev = ax.text(x, y, first[0], transform=transform or ax.transAxes, va="baseline", **{**kw, **first[1]})
    for s, style in rest:
        prev = ax.annotate(s, xy=(1, 0), xycoords=prev, va="bottom", ha="left", **{**kw, **style})


def stepped_legend(ax: plt.Axes, colors: Sequence[str], bounds: Sequence[float | str], title: str | None = None,
                   rect: tuple[float, float, float, float] = (0.0, 1.06, 0.36, 0.035)) -> plt.Axes:
    """EC class legend: a row of color blocks with boundary values under the seams.

    `bounds` has len(colors)+1 entries (numbers, strings or "" to skip).
    `rect` is in the host axes' fraction. Returns the inset axes.
    """
    t, m = theme(), media()
    lax = ax.inset_axes(rect)
    n = len(colors)
    for i, c in enumerate(colors):
        lax.add_patch(Rectangle((i, 0), 1, 1, color=c, lw=0))
        if i:
            lax.plot([i, i], [0, 1], color=t["bg"], lw=1.2)
    for i, b in enumerate(bounds):
        if b is None or b == "":
            continue
        lax.text(i, -0.4, b if isinstance(b, str) else f"{b:g}", ha="center", va="top",
                 fontsize=m["tick"], color=t["ink"], fontfamily=FONT_SANS)
    if title:
        lax.text(0, 1.5, title, ha="left", va="bottom", fontsize=m["direct"], fontweight="bold",
                 color=t["ink"], fontfamily=FONT_SERIF)
    lax.set_xlim(0, n)
    lax.set_ylim(0, 1)
    lax.axis("off")
    return lax


# ---------------------------------------------------------------------------
# Chart shapes the defaults get wrong
# ---------------------------------------------------------------------------
def lollipop_height(n: int) -> float:
    """Adaptive height for a horizontal chart with `n` categories."""
    return max(FIGSIZE_MIN_H, ROW_HEIGHT * n + 1.0)


def hlollipop(ax: plt.Axes, labels: Sequence[str], values: Sequence[float], color: str | None = None,
              colors: Sequence[str] | None = None, base: float = 0.0, filled: Sequence[bool] | None = None,
              value_fmt: Callable[[float], str] | None = None) -> None:
    """Horizontal lollipop, first label on top: stem from `base` + dot. One value per category.

    `base` != 0 or negative values give the EC diverging lollipop with an ink
    baseline; `filled=False` entries draw open rings (e.g. "not notable");
    `value_fmt` writes the value past the dot.
    """
    t = theme()
    y = np.arange(len(labels))[::-1]
    cols = list(colors) if colors is not None else [color or WINE] * len(labels)
    fill = list(filled) if filled is not None else [True] * len(labels)
    span = (max(max(values), base) - min(min(values), base)) or 1
    lw = LOLLIPOP_LW * (0.7 if _state["medium"] == "paper" else 1)
    ms = LOLLIPOP_MS * (0.85 if _state["medium"] == "paper" else 1)
    for yi, v, c, f in zip(y, values, cols, fill):
        ax.hlines(yi, base, v, color=c, linewidth=lw, zorder=3)
        ax.plot(v, yi, "o", markersize=ms, markerfacecolor=c if f else t["bg"], markeredgecolor=c,
                markeredgewidth=0 if f else 1.5, zorder=4)
        if value_fmt:
            right = v >= base
            ax.text(v + (0.04 if right else -0.04) * span, yi, value_fmt(v), va="center",
                    ha="left" if right else "right", fontsize=media()["tick"], color=t["ink"])
    ax.set_yticks(y, labels, fontfamily=FONT_SERIF, color=t["ink"])
    ax.set_ylim(-0.7, len(labels) - 0.3)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.spines["left"].set_visible(False)
    if base != 0 or min(values) < 0:
        ref_line(ax, x=base, strong=True)


def share_lollipop(labels: Sequence[str], pct: Sequence[float], ns: Sequence[float], color,
                   ax: plt.Axes | None = None, xlabel: str = "Share") -> plt.Figure:
    """Lollipop for 'share of X per group' with the n written next to each dot."""
    set_style()
    if ax is None:
        fig, ax = plt.subplots(figsize=(WIDTHS["onehalf"], lollipop_height(len(labels))))
    else:
        fig = ax.figure
    colors = color if isinstance(color, list) else [color] * len(labels)
    hlollipop(ax, labels, list(pct), colors=colors)
    for yi, p, n in zip(np.arange(len(labels))[::-1], pct, ns):
        ax.text(p + max(pct) * 0.03, yi, f"{p:.0%}  (n={int(n)})", va="center", fontsize=media()["tick"])
    ax.set_xlabel(xlabel)
    ax.set_xlim(0, max(pct) * 1.3)
    fig.tight_layout()
    return fig


def dot_strip(ax: plt.Axes, labels: Sequence[str], values: dict[str, Sequence[float]],
              colors: dict[str, str] | None = None, connect: bool = True, size: float | None = None) -> None:
    """Dumbbell / dot strip: one row per category (first on top), one dot per group, ink line min->max.

    `values` = {group: [value per label]} in a fixed order (e.g. age bands with
    the "warm" ramp). Name the groups with `rich_text` or direct labels, not a legend box.
    """
    t = theme()
    groups = list(values)
    colors = colors or dict(zip(groups, palette("house", len(groups))))
    size = size or (34 if _state["medium"] == "paper" else 60)
    y = np.arange(len(labels))[::-1]
    arr = np.array([values[g] for g in groups], dtype=float)
    if connect:
        ax.hlines(y, arr.min(axis=0), arr.max(axis=0), color=t["ink"], lw=0.7, zorder=2)
    for g, row in zip(groups, arr):
        ax.scatter(row, y, s=size, color=colors[g], edgecolors=t["ink"], linewidths=0.6, zorder=3, label=g)
    ax.set_yticks(y, labels, fontfamily=FONT_SERIF, color=t["ink"], fontweight="bold")
    ax.set_ylim(-0.7, len(labels) - 0.3)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.spines["left"].set_visible(False)


def highlight_bars(ax: plt.Axes, labels: Sequence[str], values: Sequence[float], highlight: Sequence[str] = (),
                   color: str = WINE, horizontal: bool = False,
                   value_fmt: Callable[[float], str] = "{:g}".format) -> None:
    """Context-gray bars with 1-2 accented ones and value labels; no value axis (EC 'Mishandled baggage')."""
    t, m = theme(), media()
    cols = [color if lab in highlight else t["context"] for lab in labels]
    pos = np.arange(len(labels))
    if horizontal:
        pos = pos[::-1]
        ax.barh(pos, values, color=cols, height=BAR_WIDTH * 1.3)
        for p, v in zip(pos, values):
            ax.text(v, p, value_fmt(v), va="center", ha="left", fontsize=m["tick"], color=t["ink"],
                    transform=ax.transData + _offset(ax.figure, 3, 0))
        ax.set_yticks(pos, labels, fontfamily=FONT_SERIF, color=t["ink"])
        ax.spines[["left", "bottom"]].set_visible(False)
        ax.set_xticks([])
    else:
        ax.bar(pos, values, color=cols, width=BAR_WIDTH * 1.6)
        for p, v in zip(pos, values):
            ax.text(p, v, value_fmt(v), ha="center", va="bottom", fontsize=m["tick"], color=t["ink"],
                    transform=ax.transData + _offset(ax.figure, 0, 2))
        ax.set_xticks(pos, labels, fontfamily=FONT_SERIF, color=t["ink"])
        ax.tick_params(axis="x", length=0)
        ax.spines["left"].set_visible(False)
        ax.set_yticks([])
    ax.grid(False)


def waffle(ax: plt.Axes, share: float, color: str = WINE, n: int = 100, ncols: int = 10,
           marker: str = "s", size: float = 40) -> None:
    """Unit chart: `n` marks, the first round(share*n) in `color`, the rest in context gray."""
    k = int(round(share * n))
    idx = np.arange(n)
    cols = [color if i < k else theme()["context"] for i in idx]
    ax.scatter(idx % ncols, -(idx // ncols), s=size, c=cols, marker=marker, linewidths=0)
    ax.set_aspect("equal")
    ax.axis("off")


def binned_logistic(x_raw, y, ax: plt.Axes, dot_color: str | None = None, n_bins: int = 10):
    """Logistic fit drawn as observed share per quantile bin (dot ~ n) + fitted curve with 95 % band.

    Replaces a jittered 0/1 scatter. Requires `statsmodels`; returns the LogitResults.
    """
    import pandas as pd
    import statsmodels.api as sm

    result = sm.Logit(y, sm.add_constant(x_raw)).fit(disp=False)
    dot_color = dot_color or WINE
    n_bins = min(n_bins, x_raw.nunique())
    bins = pd.qcut(x_raw, n_bins, duplicates="drop")
    binned = (pd.DataFrame({"x": np.asarray(x_raw), "y": np.asarray(y)})
              .groupby(bins.values, observed=True)
              .agg(x_mean=("x", "mean"), y_mean=("y", "mean"), n=("y", "size")))
    sizes = 18 + 90 * (binned["n"] / binned["n"].max())
    ax.scatter(binned["x_mean"], binned["y_mean"], s=sizes, color=dot_color, alpha=0.9, linewidths=0,
               zorder=3, label="Observed (binned)")
    x_line = np.linspace(x_raw.min(), x_raw.max(), 200)
    pred = result.get_prediction(sm.add_constant(x_line)).summary_frame(alpha=0.05)
    ax.fill_between(x_line, pred["ci_lower"], pred["ci_upper"], color=dot_color, alpha=0.15, linewidth=0,
                    label="95% CI")
    ax.plot(x_line, pred["predicted"], color=theme()["ink"], lw=media()["lw"], label="Logistic fit")
    ax.set_ylim(-0.03, 1.03)
    return result


# ---------------------------------------------------------------------------
# Poster composer — the ONLY place a title is baked into the pixels.
# ---------------------------------------------------------------------------
def add_poster_titles(fig: plt.Figure, title: str, subtitle: str | None = None, source: str | None = None,
                      byline: str | None = None, x: float = 0.07, top: float = 0.955) -> None:
    """EC title block: big bold serif headline, regular serif subtitle, small serif footer."""
    t = theme()
    fig.text(x, top, title, fontfamily=FONT_SERIF, fontsize=25, fontweight="bold", color=t["ink"], va="top")
    if subtitle:
        fig.text(x, top - 0.07, subtitle, fontfamily=FONT_SERIF, fontsize=13, color=t["ink"], va="top",
                 linespacing=1.0)
    foot = "\n".join(s for s in (byline, f"Source: {source}" if source else None) if s)
    if foot:
        fig.text(x, 0.02, foot, fontfamily=FONT_SERIF, fontsize=8, color=t["muted"], va="bottom", linespacing=1.05)


def compose_poster(plot_fns: Sequence[Callable[[plt.Axes], None]], title: str, subtitle: str | None = None,
                   source: str | None = None, byline: str | None = None, layout: Literal["row", "col"] = "col",
                   bg: Bg = "cream", figsize: tuple[float, float] = (7.0, 8.75)) -> plt.Figure:
    """1-2 charts + an editorial title block as one standalone image (social, slide, handout).

    Default canvas is the EC 4:5 portrait on cream. Each `plot_fn(ax)` draws a
    complete chart. Save with `save_fig(fig, path, formats="png")`.
    """
    previous = dict(_state)
    set_style(bg=bg, medium="web")
    n = len(plot_fns)
    if n not in (1, 2):
        raise ValueError("compose_poster supports exactly 1 or 2 charts")
    fig = plt.figure(figsize=figsize)
    fig.patch.set_facecolor(theme()["bg"])
    lines = subtitle.count("\n") + 1 if subtitle else 0
    top = 0.80 - 0.035 * max(0, lines - 1)
    bottom = 0.11
    if n == 1:
        axes = [fig.add_axes([0.10, bottom, 0.74, top - bottom])]
    elif layout == "row":
        w = 0.34
        axes = [fig.add_axes([0.08, bottom, w, top - bottom]), fig.add_axes([0.54, bottom, w, top - bottom])]
    else:
        h = (top - bottom - 0.08) / 2
        axes = [fig.add_axes([0.10, bottom + h + 0.08, 0.74, h]), fig.add_axes([0.10, bottom, 0.74, h])]
    for fn, ax in zip(plot_fns, axes):
        ax.set_facecolor(theme()["bg"])
        fn(ax)
    add_poster_titles(fig, title, subtitle, source, byline)
    _state.update(previous)
    set_style()
    return fig


# Backwards-compatible names used by older projects (HolidayCalc, GeoGram).
INK_COLOR = SURFACES["white"]["ink"]
MUTED_COLOR = SURFACES["white"]["muted"]
BG_WHITE, BG_CREAM = SURFACES["white"]["bg"], SURFACES["cream"]["bg"]
