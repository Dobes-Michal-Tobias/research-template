"""Render the style specimen: every palette and one example per chart recipe.

    python -m modules.dataviz_style.gallery            # -> modules/dataviz_style/gallery/*.png

Synthetic data with a fixed seed; the point is the look, not the numbers.
Each function is also a copy-paste starting point for a project's `viz.py`.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from modules.dataviz_style import chartstyle as cs

OUT = Path(__file__).resolve().parent / "gallery"
RNG = np.random.default_rng(7)


def _save(fig: plt.Figure, name: str) -> None:
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / f"{name}.png", dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)


# --- palettes ---------------------------------------------------------------
def palettes_sheet() -> None:
    """Swatches of every palette on both surfaces, with hex codes and roles."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 8.2))
    for ax, bg in zip(axes, ("white", "cream")):
        cs.set_style(bg=bg, medium="web")
        t = cs.theme()
        ax.set_facecolor(t["bg"])
        ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, color=t["bg"], zorder=-1))
        ax.axis("off")
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 23)
        y = 22
        ax.text(0, y, f"{bg} surface  {t['bg']}", fontfamily=cs.FONT_SERIF, fontsize=12, fontweight="bold",
                color=t["ink"], va="center")
        y -= 1.4
        rows = [(f"categorical · {k}", v["colors"]) for k, v in cs.CATEGORICAL.items()]
        rows += [(f"sequential · {k}", v) for k, v in cs.SEQUENTIAL.items()]
        rows += [(f"diverging · {k}", v) for k, v in cs.DIVERGING.items()]
        rows += [("neutrals · ink muted rule context land", [t["ink"], t["muted"], t["rule"], t["context"], t["land"]])]
        for name, cols in rows:
            ax.text(0, y + 0.55, name, fontfamily=cs.FONT_SERIF, fontsize=8.5, color=t["ink"], va="bottom")
            w = 10 / max(len(cols), 1)
            for i, c in enumerate(cols):
                ax.add_patch(Rectangle((i * w, y - 0.6), w * 0.94, 1.1, color=c, lw=0))
                ax.text(i * w + 0.08, y - 0.5, c, fontsize=6.3, fontfamily=cs.FONT_MONO,
                        color="#ffffff" if _dark(c) else t["ink"], va="bottom")
            y -= 1.75
        # demo of a context line + highlighted line on this surface
        x = np.linspace(0, 10, 50)
        for k in range(6):
            ax.plot(x, y - 0.8 + 0.5 * np.sin(x / 2 + k), color=t["context"], lw=0.9)
        ax.plot(x, y - 0.8 + 0.6 * np.sin(x / 2.5), color=cs.WINE, lw=2)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, wspace=0.06)
    fig.patches.append(Rectangle((0.5, 0), 0.5, 1, transform=fig.transFigure, color=cs.SURFACES["cream"]["bg"],
                                 zorder=-2))
    fig.patch.set_facecolor(cs.SURFACES["white"]["bg"])
    _save(fig, "00_palettes")


def _dark(hex_color: str) -> bool:
    from modules.dataviz_style.palette_check import oklch
    return oklch(hex_color)[0] < 0.6


# --- recipes ----------------------------------------------------------------
def line_highlight_context(bg: str = "white") -> None:
    """EC 'Turn the AC on': many context lines, 3 highlighted series, ink average, end dots + labels."""
    cs.set_style(bg=bg, medium="paper")
    t = cs.theme()
    years = np.arange(2015, 2025)
    fig, ax = plt.subplots(figsize=cs.figsize("onehalf", 0.6))
    base = 100 * np.cumprod(1 + RNG.normal(0.06, 0.08, (14, len(years))), axis=1)
    base[:, 0] = 100
    cs.context_lines(ax, years, base)
    focus = {"Czechia": cs.WINE, "Hungary": cs.GOLD, "Finland": cs.VIOLET}
    ends = []
    for k, (name, color) in enumerate(focus.items()):
        y = 100 * np.cumprod(1 + RNG.normal(0.14 - 0.03 * k, 0.12, len(years)))
        y[0] = 100
        ax.plot(years, y, color=color, zorder=4)
        ends.append((years[-1], y[-1], name, color))
    avg = base.mean(axis=0)
    ax.plot(years, avg, color=t["ink"], lw=cs.media()["lw"] * 1.1, zorder=5)
    ends.append((years[-1], avg[-1], "EU average", t["ink"]))
    cs.ref_line(ax, y=100, strong=True)
    ax.set_xlim(years[0] - 0.3, years[-1] + 0.2)
    ax.set_ylim(60, None)
    cs.direct_labels(ax, ends, dots=True)
    cs.gridline_labels(ax, unit="index (2015 = 100)")
    ax.set_xticks(years[::2])
    _save(fig, f"01_line_highlight_context_{bg}")


def annotated_series(bg: str = "cream") -> None:
    """EC 'Crude prices' / 'Out-of-office': one series, event rules with notes, a highlighted period."""
    cs.set_style(bg=bg, medium="web")
    fig, ax = plt.subplots(figsize=cs.figsize("web", 0.62))
    x = np.arange(520)
    noise = np.cumsum(RNG.normal(0, 1.1, len(x)))
    level = np.select([x < 205, x < 225, x < 300, x < 315, x < 430],
                      [55, 55 - 1.7 * (x - 205), 21 + 0.45 * (x - 225), 55 + 3.6 * (x - 300), 100 - 0.25 * (x - 315)],
                      70 + 0.0 * x)
    noise -= np.linspace(noise[0], noise[-1], len(x))  # no drift: keep the story in `level`
    y = np.clip(level + noise, 8, None)
    ax.plot(x, y, color=cs.APRICOT, lw=1.3)
    ax.set_xlim(0, 520)
    ax.set_ylim(0, 130)
    cs.highlight_span(ax, 470, 500, color=cs.APRICOT)
    cs.event_line(ax, 222, "COVID-19 pandemic", "Price drops by about 70 %\nin two months", top=0.86)
    cs.event_line(ax, 312, "Full-scale invasion", "Price reaches 110 USD", top=1.0)
    cs.callout(ax, xy=(470, 100), xytext=(445, 125), text="A highlighted period:\nthe band fades upwards",
               ha="right")
    cs.gridline_labels(ax, ticks=[0, 20, 40, 60, 80, 100, 120], unit="USD per barrel")
    ax.set_xticks([0, 104, 208, 312, 416, 520], ["2016", "2018", "2020", "2022", "2024", "2026"])
    _save(fig, f"02_annotated_series_{bg}")


def small_multiples_ci(bg: str = "white") -> None:
    """Paper figure: panels with CI bands, method identity by color, variants by line style, letters a/b."""
    cs.set_style(bg=bg, medium="paper")
    ns = np.array([100, 250, 500, 1000, 2000, 5000])
    fig, axes = plt.subplots(1, 2, figsize=cs.figsize("double", 0.36), sharey=True)
    methods = [("Hapax", cs.WINE, cs.SOLID, -0.05), ("Hapax, inductive", cs.WINE, cs.DASHED, -0.22),
               ("Delta", cs.GOLD, cs.SOLID, 0.08), ("Char n-grams", cs.GREEN, cs.SOLID, 0.25),
               ("Baseline", cs.theme()["context"], cs.SOLID, 0.15)]
    for k, (ax, title) in enumerate(zip(axes, ("Random words", "Contiguous passage"))):
        cs.ref_line(ax, y=0.5)
        ends = []
        for name, color, ls, shift in methods:
            m = 0.5 + 0.45 / (1 + np.exp(-(np.log(ns) - 6.6 + 4 * shift))) - 0.06 * k
            ctx = color == cs.theme()["context"]
            if not ctx:
                ax.fill_between(ns, m - 0.025, m + 0.025, color=color, alpha=0.13, lw=0)
            ax.plot(ns, m, color=color, ls=ls, lw=cs.media()["lw_context" if ctx else "lw"], marker="o",
                    markersize=2.4, markeredgewidth=0, zorder=2 if ctx else 3)
            ends.append((ns[-1], m[-1], name, color))
        ax.set_xscale("log")
        ax.set_xticks(ns, [f"{n:,}".replace(",", " ") for n in ns])
        ax.minorticks_off()
        ax.set_ylim(0.4, 1.0)
        ax.set_xlabel("Sample length N (words, log scale)")
        cs.panel_title(ax, title, x=0.04)
        cs.panel_letter(ax, "ab"[k], x=0.0)
        if k == 1:
            cs.direct_labels(ax, ends, min_gap=0.06)
    axes[0].set_ylabel("Accuracy (pairwise)")
    fig.tight_layout()
    _save(fig, f"03_small_multiples_ci_{bg}")


def dot_strip_groups(bg: str = "cream") -> None:
    """EC 'Old and grumpy': ordinal groups in the warm ramp, shaded row groups, legend inside a sentence."""
    cs.set_style(bg=bg, medium="web")
    t = cs.theme()
    labels = ["Anger", "Anxiety", "Helplessness", "Frustration", "Determination", "Serenity", "Hope"]
    groups = ["15–24", "25–39", "40–54", "55+"]
    colors = dict(zip(groups, cs.SEQUENTIAL["warm"]))
    vals = {g: [0] * 7 for g in groups}
    for i, g in enumerate(groups[1:], 1):
        vals[g] = list(np.r_[RNG.uniform(10, 60, 4) * i, -RNG.uniform(3, 12, 3) * i])
    fig, ax = plt.subplots(figsize=cs.figsize("web", 0.72))
    ax.add_patch(Rectangle((0, 2.5), 1, 4.2, transform=ax.get_yaxis_transform(), color=t["panel"], lw=0, zorder=0))
    cs.dot_strip(ax, labels, vals, colors)
    cs.ref_line(ax, x=0)
    ax.text(0.99, 2.7, "Negative emotions", transform=ax.get_yaxis_transform(), ha="right", fontfamily=cs.FONT_SERIF,
            style="italic", color=cs.ROSE, fontsize=cs.media()["direct"])
    ax.text(0.99, -0.5, "Positive emotions", transform=ax.get_yaxis_transform(), ha="right", fontfamily=cs.FONT_SERIF,
            style="italic", color=cs.SEQUENTIAL["sage"][4], fontsize=cs.media()["direct"])
    segs = []
    for g in groups:
        segs += [("● ", {"color": colors[g], "fontfamily": "DejaVu Sans"}), (f"{g} years   ", {"fontweight": "bold"})]
    cs.rich_text(ax, 0, 1.06, segs)
    ax.set_xlabel("Difference from the 15–24 group (%)")
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:+.0f}%".replace("-", "−"))
    _save(fig, f"04_dot_strip_groups_{bg}")


def diverging_lollipop(bg: str = "white") -> None:
    """EC 'Is fake meat bad for you?': stems from zero, filled = notable, open = not, values at the dots."""
    cs.set_style(bg=bg, medium="paper")
    labels = ["Carbohydrates", "Fiber", "Sugars", "Salt", "Unsaturated fat", "Protein", "Saturated fat"]
    vals = [7.3, 4.0, 1.1, 0.0, -2.4, -4.3, -4.9]
    filled = [False, True, False, False, False, False, True]
    fig, ax = plt.subplots(figsize=cs.figsize("onehalf", 0.62))
    cs.hlollipop(ax, labels, vals, color=cs.VIOLET, filled=filled,
                 value_fmt=lambda v: f"{v:+.1f} g".replace("-", "−") if v else "±0 g")
    ax.set_xlim(-7.5, 9.5)
    ax.set_xlabel("Plant-based minus meat, grams per 100 g")
    _save(fig, f"05_diverging_lollipop_{bg}")


def highlight_bars_demo(bg: str = "cream") -> None:
    """EC 'Mishandled baggage': gray bars, one accent, values on bars, callout instead of an axis."""
    cs.set_style(bg=bg, medium="web")
    fig, ax = plt.subplots(figsize=cs.figsize("web", 0.42))
    labels = ["Africa", "Europe", "Americas", "Middle East", "Asia-Pacific"]
    vals = [12.1, 10.5, 5.6, 5.0, 3.1]
    cs.highlight_bars(ax, labels, vals, highlight=["Europe"], color=cs.ROSE)
    cs.callout(ax, xy=(1.4, 10.5), xytext=(2.0, 12.6), title="Europe's high rate",
               text="is partly down to its many\nconnecting flights")
    ax.set_ylim(0, 14)
    cs.unit_label(ax, "Mishandled bags per 1,000 passengers", y=1.02)
    _save(fig, f"06_highlight_bars_{bg}")


def waffles(bg: str = "cream") -> None:
    """EC 'Male dominated violence': small-multiple unit charts with the value in the panel title."""
    cs.set_style(bg=bg, medium="web")
    fig, axes = plt.subplots(1, 4, figsize=cs.figsize("web", 0.3))
    for ax, (name, share) in zip(axes, [("Spain", 0.82), ("France", 0.89), ("Germany", 0.82), ("Sweden", 0.81)]):
        cs.waffle(ax, share, color=cs.ROSE, size=22)
        cs.panel_title(ax, f"{name} – {share:.0%}", y=1.04)
    _save(fig, f"07_waffles_{bg}")


def grid_maps(bg: str = "white") -> None:
    """Choropleth stand-ins: a sequential and a diverging grid with EC stepped legends."""
    cs.set_style(bg=bg, medium="paper")
    t = cs.theme()
    fig, axes = plt.subplots(1, 2, figsize=cs.figsize("double", 0.42))
    yy, xx = np.mgrid[0:14, 0:20]
    field = np.exp(-((xx - 12) ** 2 + (yy - 6) ** 2) / 30) + 0.15 * RNG.random(xx.shape)
    mask = RNG.random(xx.shape) < 0.12
    for ax, (name, data, bounds, title) in zip(axes, [
        ("wine", field, ["0", "", "", "", "", "", "1,000+"], "Strikes per cell"),
        ("violet_gold", (field - np.median(field)) * 3, ["−200 %", "", "", "", "", "", "", "", "", "+200 %"],
         "Change vs. baseline"),
    ]):
        steps = len(cs.SEQUENTIAL.get(name) or cs.DIVERGING[name])
        c = cs.cmap(name, steps=steps)
        img = np.ma.masked_where(mask, data)
        ax.add_patch(Rectangle((-0.5, -0.5), 20, 14, color=t["land"], lw=0, zorder=0))
        ax.pcolormesh(np.arange(21) - 0.5, np.arange(15) - 0.5, img, cmap=c, edgecolors=t["bg"], linewidth=0.6,
                      vmin=-1 if name != "wine" else 0, vmax=1 if name != "wine" else field.max())
        ax.set_aspect("equal")
        ax.axis("off")
        cs.stepped_legend(ax, cs.palette(name), bounds, title=title, rect=(0.0, 1.13, 0.5, 0.05))
    fig.tight_layout()
    _save(fig, f"08_grid_maps_{bg}")


def poster() -> None:
    """Standalone social image (cream, 4:5): serif headline + subtitle + footer around one chart."""
    years = np.arange(1990, 2026)

    def chart(ax):
        t = cs.theme()
        series = {"renewables": cs.JADE, "gas": cs.APRICOT, "lignite": cs.PLUM, "nuclear": cs.ROSE}
        ends = []
        for k, (name, color) in enumerate(series.items()):
            trend = [np.linspace(20, 290, len(years)), np.linspace(35, 85, len(years)),
                     np.linspace(170, 75, len(years)), np.r_[np.full(25, 160), np.linspace(160, 0, 11)]][k]
            y = np.clip(trend + RNG.normal(0, 6, len(years)), 0, None)
            ax.plot(years, y, color=color, lw=2.2)
            ends.append((years[-1], y[-1], name, color))
        ax.set_xlim(1990, 2025.5)
        ax.set_ylim(0, 310)
        ax.grid(axis="y", ls=(0, (2, 3)), color=t["rule"])
        cs.direct_labels(ax, ends)
        cs.gridline_labels(ax, ticks=[0, 100, 200, 300], unit="terawatt hours")
        ax.set_xticks([1990, 2000, 2010, 2020])

    fig = cs.compose_poster([chart], title="German electricity",
                            subtitle="Renewables now cover nearly two-thirds\nof electricity production",
                            byline="michaltobiasdobes.cz | Michal Tobiáš Dobeš", source="synthetic demo data")
    _save(fig, "09_poster_cream")


def main() -> None:
    palettes_sheet()
    line_highlight_context("white")
    line_highlight_context("cream")
    annotated_series("cream")
    small_multiples_ci("white")
    dot_strip_groups("cream")
    diverging_lollipop("white")
    highlight_bars_demo("cream")
    waffles("cream")
    grid_maps("white")
    poster()
    print(f"gallery written to {OUT}")


if __name__ == "__main__":
    main()
