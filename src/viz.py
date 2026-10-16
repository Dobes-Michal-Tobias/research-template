"""Visualization module.

Convention for this project (see principles.md): all plotting logic lives
here, not in notebooks. Notebooks only call functions defined in this file
and display/save the result.

The look comes from the house style in `modules/dataviz_style` — read its
`STYLE_GUIDE.md` before writing a chart (palettes and their roles, paper vs
web, annotation helpers, chart catalogue). Map the project's categories to
colours once, in `src/config.py` or at the top of this file, and never let
the plotting library assign colours by order.

Every plotting function should:
  - accept data + an optional `ax` (so it composes into subplots/grids)
  - call `set_style()` with no arguments (keeps the notebook's bg/medium)
  - return the Figure it drew on, never set an in-axes title
  - be saved via `save_fig()` instead of ad-hoc savefig calls
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

from modules.dataviz_style import chartstyle as cs
from modules.dataviz_style.chartstyle import set_style  # noqa: F401  (re-exported for notebooks)
from src.config import REPORTS_FIGURES

PALETTE = cs.palette("house")   # wine, gold, green, violet — see STYLE_GUIDE.md §3


def save_fig(fig: plt.Figure, name: str, subdir: str | None = None,
             formats: tuple[str, ...] | str | None = None) -> list[Path]:
    """Save under reports/figures/[subdir/]name.* (paper: pdf+svg+png, web: svg)."""
    out_dir = REPORTS_FIGURES / subdir if subdir else REPORTS_FIGURES
    return cs.save_fig(fig, out_dir / name, formats=formats)


def plot_barplot(
    data,
    x: str,
    y: str,
    hue: str | None = None,
    title: str | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Generic example plot — replace/extend with project-specific charts.

    Kept minimal on purpose: this file should not accumulate every possible
    chart type "just in case". Add functions here as the project actually
    needs them. `title` is drawn as a panel title (notebook use); figures
    for a paper or a page carry their title in the caption instead.
    """
    set_style()
    if ax is None:
        _, ax = plt.subplots(figsize=cs.figsize("onehalf"))
    n_hue = data[hue].nunique() if hue else 1
    sns.barplot(data=data, x=x, y=y, hue=hue, ax=ax, width=cs.BAR_WIDTH * 1.4,
                palette=PALETTE[:n_hue] if hue else None, color=None if hue else PALETTE[0],
                err_kws={"color": cs.theme()["ink"], "linewidth": 0.8})
    if title:
        cs.panel_title(ax, title)
    ax.tick_params(axis="x", rotation=30, length=0)
    ax.spines["left"].set_visible(False)
    if hue:
        ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    return ax
