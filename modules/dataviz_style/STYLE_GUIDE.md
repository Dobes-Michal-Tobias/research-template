# Chart style guide

The house style for every chart I make: journal papers, the thesis, slides,
my personal website and social posts. It is **editorial data journalism**
in the register of *The European Correspondent* (EC), the FT and Our World
in Data: a chart that reads as reporting, not as a default export. Thin
marks, few colours with fixed meanings, labels next to the data instead of
in a legend box, annotations that say what to see, and no chrome that does
not carry information.

The rules come from three sources, in this order of authority:

1. **What worked in my projects** — `HolidayCalc` (palette, fills, calendar
   charts) and `AuthorshipProvenance/01_eval_hapax_rozdelene_slovniky`
   (paper figures: method identity colours, context lines, CI bands, serif
   direct labels, small multiples). Lessons learnt there are marked
   *(lesson)*.
2. **The EC reference set** (~95 Instagram charts collected in
   `~/Downloads/plots`) — typography, annotation, chart forms, maps.
3. **Computation** — every palette passes `palette_check.py` (lightness,
   chroma, colour-vision-deficiency separation, contrast). Hex values are
   not chosen by eye alone.

`gallery/` shows every rule rendered (`python -m modules.dataviz_style.gallery`);
when unsure what "in style" means, copy the closest gallery function.

---

## 1. Two contexts, one style

The style is the same everywhere; four things change with the destination.

| | **Paper** (journal, thesis, PDF, slides) | **Web** (personal site, essay) | **Poster** (social, handout) |
|---|---|---|---|
| `set_style(...)` | `bg="white", medium="paper"` | `bg="white"` or `"cream", medium="web"` | `compose_poster(..., bg="cream")` |
| Background | white `#ffffff` — **always** | white by default; cream `#f3eeeb` if the page is cream | cream (EC canvas) |
| Title / subtitle | in the caption, never in the image | in `<h2>` / `<figcaption>`, never in the image | baked in: serif headline + subtitle + footer |
| Size | final print size: 3.5 in single column, 5.5 in 1.5-column, 7.2 in double (`figsize("single")`) | 7 in wide (`figsize("web")`), scales down on phones | 7 × 8.75 in = 4:5 portrait (1080 × 1350 px at 154 dpi) |
| Text size at final size | 7–9 pt (`MEDIA["paper"]`) | 8.5–10 pt (`MEDIA["web"]`) | headline 25 pt, subtitle 13 pt |
| Files | PDF (submission) + SVG + PNG preview | SVG | PNG |
| Panel letters | **a**, **b** when the text refers to panels | no | no |

**Why cream never goes into a paper:** journals print on white, reviewers
read on white, a tinted rectangle in a white PDF looks like a pasted
screenshot, and some publishers reject coloured figure backgrounds outright.
Cream is a *site identity* choice: use it only when the surrounding page is
cream too, otherwise the chart becomes a visible card.

Pick the background per **project / page**, not per chart. A page mixing
white and cream charts looks like a mistake.

---

## 2. The ten rules

1. **A colour is a role, not a decoration.** One method / group / category
   keeps one colour in every figure of a project, assigned by identity in a
   `config.py` dict — never by plotting order or the library's colour cycle.
2. **Few colours.** 1–4 strong hues per chart. Everything else is *context*:
   light warm gray. More than 4 categories → small multiples or
   highlight-plus-context, never a 7-colour legend.
3. **Variants share the colour of their family and differ by line style**
   (solid / dashed / dotted / dash-dot). *(lesson: "Hapax", "Hapax prior",
   "Hapax inductive" were all wine; readers grouped them instantly.)*
4. **Label the data directly.** Text at the end of the line, next to the
   dot, inside the bar. A legend box is the fallback, not the default.
5. **Say what to see.** A short annotation with a thin leader line beats a
   paragraph in the caption. The headline states the finding, not the
   variables ("Contiguous passages are harder", not "Accuracy by N").
6. **Remove chrome until it hurts.** No top/right spines, one grid
   direction, no frame around the legend, no background panel, no
   gradients on bars, no 3-D, no drop shadows.
7. **Thin marks.** Lines 1.5 pt (paper) / 2 pt (web); bars half as wide as
   the default; a lollipop instead of a bar when there is one value per
   category.
8. **Ink hierarchy.** Data in colour, reference lines in light gray (dotted),
   zero baseline in solid ink, text in warm near-black, ticks in muted gray.
   A gray series is *context*, and its label is a darker gray.
9. **Uncertainty is shown, quietly.** CI bands at α ≈ 0.13 for highlighted
   series only, never for context lines.
10. **Validated, not guessed.** New colours go through
    `python -m modules.dataviz_style.palette_check` before they ship.

---

## 3. Colour

### 3.1 Neutrals (per surface)

Every neutral is defined twice, because gray that works on white turns
muddy on cream. Read them via `theme()`; never hard-code.

| token | role | white | cream |
|---|---|---|---|
| `bg` | canvas | `#ffffff` | `#f3eeeb` |
| `ink` | text, zero baseline, leader lines, the "average" series | `#2b2522` | `#1f1a17` |
| `muted` | tick labels, footer, secondary text | `#7a726c` | `#6e665f` |
| `grid` | gridlines | `#ece8e2` | `#e2dbd5` |
| `rule` | reference lines: chance, mean (dotted) | `#d6d0c8` | `#cfc7bf` |
| `context` | context series / non-highlighted bars | `#c4bdb4` | `#bfb7ae` |
| `context_text` | labels of context series | `#8a827a` | `#857c74` |
| `land` | map land without data | `#e4e1dc` | `#d4d4d4` (EC) |
| `panel` | shaded block behind a group of rows | `#f7f4f0` | `#ebe4df` |

Warm grays only (a hint of red-brown), never cool blue-grays: the palette
is warm, and a cool gray next to wine looks dirty.

### 3.2 Categorical palettes

All three are 4 slots, validated on both surfaces (all pairs, not just
neighbours). Order = assignment priority for a *new* project; once a
project maps a category to a colour, that mapping is fixed.

**`house` — the default** (lines, dots, small marks; papers and web)

| slot | name | hex | typical role |
|---|---|---|---|
| 1 | wine | `#a61b57` | the main subject (my method, the focus country) |
| 2 | gold | `#b07d00` | the main competitor / baseline family |
| 3 | green | `#1ea381` | a third family; "good", positive outcome |
| 4 | violet | `#a35ec1` | a fourth family; the extension / new variant |

Checks: lightness 0.43–0.77, chroma ≥ 0.10, worst CVD ΔE 11.7 (gold vs
green, deutan), all ≥ 3:1 on white. On cream green drops to 2.8:1, so green
lines on cream always get a direct label.

**`editorial` — the softer EC register** (web essays; also fine in papers)

| rose `#af535f` | apricot `#dfa044` | jade `#29a987` | plum `#723c7e` |
|---|---|---|---|

Dustier and warmer than `house`, closest to EC's own charts. Apricot and
jade are below 3:1 → never as thin lines without labels; use them for
thick lines, areas, dots with labels.

**`pastel` — HolidayCalc fills** (bars, areas, calendar cells, Gantt strips)

| yellow `#f4c54d` | mint `#69c2a4` | mauve `#a885a6` | wine `#a61b57` |
|---|---|---|---|

Light fills, contrast 1.4–2.8:1 by design. Text on or next to them uses the
darker **text twins**: yellow → `#b07d00`, mint → `#097d5a`
(`label_color()` does the mapping). Wine stays the *anomaly* colour in
this set (HolidayCalc: the record, the deviation, the false claim).

### 3.3 Sequential ramps (ordered values, light → dark)

| name | steps | use |
|---|---|---|
| `wine` | `#fbe6ea` → `#3d0a22` (6) | default for counts, rates, intensity |
| `gold` | `#fdf1cc` → `#7a5500` (6) | HolidayCalc ordinal slots, "warmth" |
| `sage` | `#e6e8d4` → `#2f5446` (6) | nature, land, positive quantity (EC "Ancient forests") |
| `ember` | `#fbebb8` → `#261535` (6) | density heatmaps, hot spots (EC "Thunderbolt"); dark = most |
| `warm` | apricot → salmon → rose → plum (4) | **ordinal groups** such as age bands (EC "Old and grumpy") |

Use stepped classes (`cmap(name, steps=5)`) for maps and heatmaps — EC
never uses continuous gradients on maps, and classes can be read off the
legend. Continuous only for dense fields where steps would band.

### 3.4 Diverging ramps (sign matters: above / below a midpoint)

| name | arms | use |
|---|---|---|
| `violet_gold` | violet ← neutral `#eeeae4` → gold | default |
| `plum_apricot` | plum ← neutral → apricot | warmer, editorial pages |

**Why only purple ↔ gold:** EC's diverging maps use rose ↔ dusty blue, and
blue is out of my palette. Every blue-free alternative I tested
(wine/green, wine/teal, wine/sage, wine/gray) collapses for deuteranopes
at equal lightness (mirrored-step ΔE 0.4–7) — the sign of the value would
vanish for ~5 % of male readers. Purple ↔ gold/orange survives (ΔE 10–29).
Do not invent a red–green diverging scale "just for this map".

### 3.5 Highlight + context (the most used EC pattern)

When there are many series but the story is about 1–3 of them: draw all
others in `context` at ~70 % line width, the 1–3 in palette colours, and a
summary series (EU average, overall mean) in **ink**, with end dots and
direct labels (gallery `01`). Context series may carry labels in
`context_text` when a reader needs to find a specific one (EC "Falling
scores"). Same idea for bars: all gray, one accented (gallery `06`).

### 3.6 What is not in the palette, on purpose

- **No blue, no terracotta** as series colours. Steelblue is every default
  library's first colour (reads as "default export"); terracotta was the old
  template's alarm colour and clashes with wine. (EC uses both; this style
  replaces them with violet and wine / apricot.)
- **No rainbow, no viridis/jet by default**, no seaborn "deep".
- **Gray is never a main series.** Light gray means "context".
- **Ink (near-black) is a text colour**, and the only series allowed in ink
  is the reference/summary series (average, total).

### 3.7 Validation

```
python -m modules.dataviz_style.palette_check            # all named palettes, both surfaces
python -m modules.dataviz_style.palette_check "#a61b57,#1ea381" "#f3eeeb"
```

Thresholds (from the dataviz skill): OKLCH lightness 0.43–0.77 for line
colours, chroma ≥ 0.10, CVD ΔE ≥ 8 target / ≥ 6 floor (Machado 2009,
protan + deutan), normal-vision ΔE ≥ 15, contrast ≥ 3:1 or the series
needs direct labels; ramps must be monotonic in lightness with
steps ≥ 0.04; diverging mirrored steps must stay ≥ 8 apart under CVD.
A project that adds colours documents the `palette_check` run in its
README. *(lesson: project 01 validated its four method colours this way
before any figure went to the supervisor.)*

---

## 4. Typography

| font | job | never |
|---|---|---|
| **IBM Plex Serif** | direct labels, callouts, panel titles, category labels on the y axis, poster headline / subtitle / footer, the unit label | tick numbers |
| **IBM Plex Sans** | tick labels, axis titles, panel letters, values printed on marks | headlines |
| **IBM Plex Mono** | code-like metadata only (run id, commit hash) | anything a reader reads as prose |

This is EC's split (serif voice + clean numbers) adapted to Plex, which my
site already loads. All `.ttf` files are bundled in `fonts/` and registered
by `set_style()`; without them matplotlib silently falls back to DejaVu
Sans — the single biggest "this is a default export" tell.

- **Weights:** regular for text; **bold** for panel titles, the key phrase
  in a callout, the poster headline, and category labels in dot strips.
  Italic for explanatory notes (event notes, "Negative emotions" group
  labels). No semibold serif (matplotlib registers it as a separate family).
- **Leading:** matplotlib's `linespacing=1.0` already gives 1.3 em; values
  above ~1.05 look double-spaced. Keep 1.0.
- **Case:** sentence case everywhere. No ALL CAPS except acronyms.
- **Numbers:** thin space as thousands separator in English papers
  (`1 000`, or `1,000` in web/EC style — pick one per project); true minus
  `−` not hyphen (`axes.unicode_minus`); units once, at the top of the axis.
  Czech pages: decimal comma (`_dec()` helper in HolidayCalc).
- **Colour of text:** labels take the colour of their series (via
  `label_color()` so light fills get darker twins); everything else ink or
  muted.

---

## 5. Axes and chrome

- **Spines:** left and bottom only, ink, 0.7 pt (paper) / 0.9 pt (web).
  Drop the left spine when the value axis is replaced by gridline labels,
  for horizontal category charts, and for bar charts with values on bars.
- **Grid:** one direction, along the value axis, `grid` token, 0.6–0.8 pt.
  EC variant for posters: dotted gridlines in `rule`.
- **Gridline labels (EC):** the numbers sit *on* the gridlines at the left
  edge, inside the plot, with the unit appended to the top one ("120 USD per
  barrel") — `gridline_labels(ax, unit=...)`. Saves the rotated y label and
  the left margin; use on web/posters and in papers when there is one panel.
- **Unit label:** if not appended to the top gridline, a horizontal serif
  bold label above the axis (`unit_label`), not a rotated `ylabel`. Paper
  small multiples keep a normal rotated `ylabel` on the first panel
  (journals expect it).
- **Zero baseline** is solid ink (`ref_line(ax, y=0, strong=True)`);
  other references (chance 0.5, average) are dotted `rule` with an optional
  right-aligned label.
- **Axis not starting at zero:** draw the zigzag `axis_break(ax)` (EC) on
  bar-like readings; lines may start anywhere without it.
- **Ticks:** x ticks short (3 pt) and muted; no y ticks. Log axes get
  explicit tick positions and only well-spaced labels *(lesson:
  `_log_n_axis` in project 01 — every N a tick, only 100/250/500/1 000/…
  a label)*.
- **Limits:** pad the end so direct labels have room (`set_xlim(..., x_last
  + 3–5 %)`), not so the data floats in empty space.

---

## 6. Labels, legends, annotations

**Direct labels** (`direct_labels`): serif, series colour, right of the line
end, nudged apart vertically so they never overlap; `dots=True` adds the EC
end dot. In small multiples label only the last panel.

**Legend inside a sentence** (`rich_text`): colour the key words of the
subtitle or a line above the plot ("**Real meat** and **plant-based
meats** are different beasts") or a row of coloured dots + bold group names
(gallery `04`). Replaces the legend box for ≤ 4 groups.

**When a legend box is unavoidable** (many line styles, symbols that cannot
be labelled at the end): frameless, below the plot (`fig.legend(...,
loc="lower center", ncol=…)`), `handlelength=2.6` so dash patterns are
readable.

**Callouts** (`callout`): thin ink leader (0.7 pt) with a right-angle elbow,
text in serif, optional **bold title** line above it, halo in the
background colour so it stays readable over lines. Point at one specific
datum; one to three per chart.

**Event lines** (`event_line`): vertical ink rule from the axis up to a
bold title and italic note above the plot (EC "Crude prices").

**Highlighted period** (`highlight_span`): a band in a light palette colour
fading towards the top (EC "Out-of-office"), annotated once.

**Group panels:** a `panel`-coloured rectangle behind a block of rows, the
group name in italic in the panel corner, coloured by meaning (EC
"Negative / Positive emotions").

**Panel titles** (`panel_title`) name the panel in serif bold above its
top-left corner; **panel letters** (`panel_letter`) are for papers only.

---

## 7. Chart catalogue

Choose by the question, then use the recipe. `gallery/NN_*` shows each;
EC references in quotes.

| Question | Form | Helper / recipe | Gallery |
|---|---|---|---|
| How did a few series develop, against many? | line, highlight + context, end dots | `context_lines`, `direct_labels(dots=True)`, `gridline_labels` | `01` |
| What happened when? | single series + event lines, highlighted span | `event_line`, `highlight_span`, `callout` | `02` |
| How do methods compare across a parameter, with uncertainty? | small multiples, CI bands, variants by line style | `panel_title`, `panel_letter`, `ref_line`, `direct_labels` | `03` |
| How do ordered groups differ per category? | dot strip / dumbbell, warm ramp, group panels | `dot_strip`, `rich_text` | `04` |
| Difference from a reference, per item | diverging lollipop, filled = notable, open = not | `hlollipop(base=0, filled=…)` | `05` |
| Ranking / one value per category | lollipop (not a bar) | `hlollipop`, `lollipop_height(n)` | — |
| One category vs the rest | gray bars, one accent, values on bars, no axis | `highlight_bars` | `06` |
| Share of a whole, made tangible | waffle / unit chart, small multiples | `waffle` | `07` |
| Values over a grid / regions | stepped choropleth or grid map, EC pill legend | `cmap(name, steps)`, `stepped_legend` | `08` |
| A standalone shareable image | poster: headline + subtitle + chart + footer | `compose_poster` | `09` |
| Composition (part-to-whole) | thin stacked bar (`BAR_WIDTH`), white 2 px seams, segment values only if they fit, total in bold at the end | HolidayCalc `plot_summer_by_weekday` | — |
| Relationship of two variables | scatter: dots with a 0.6 pt ink or bg edge, size legend as nested circles, quadrant shading in `panel`, 2–3 named points with callouts ("Heavy burden", "Participation for productivity") | matplotlib + `callout` | — |
| Binary outcome vs a predictor | binned proportions + logistic fit + band | `binned_logistic` | — |
| Distribution per group | dots per item (jittered) + ink median tick *(lesson: project 01 `plot_corpus_overview`)*; ridgeline for many time series ("Heat kills": fill above baseline in a sequential tint, below in context) | matplotlib | — |
| Accuracy vs coverage, trade-offs | curve per method + fixed operating points as large dots with bg edge and a callout *(lesson: project 01 `plot_risk_coverage`)* | matplotlib + `callout` | — |
| 2-D embedding (MDS, PCA) | equal aspect; filled dots = training, rings = test; decision regions tinted at α 0.07, boundary dashed ink; errors as ink × *(lesson: `plot_mds_map`)* | matplotlib | — |
| Categorical sequence over time | stripe / barcode chart: one thin bar per period in category colour ("Furniture lost its colour") | `ax.bar(width=0.6)` | — |

Forms to avoid: pie and donut (use waffle or one bar), radial / circular
bar charts (pretty, unreadable), dual y axes (two panels instead), stacked
areas with > 4 layers, 3-D anything, word clouds.

---

## 8. Uncertainty

- Bands: `fill_between(lo, hi, alpha=0.13, lw=0)` in the series colour,
  drawn below the line (`zorder` one less). Context series get no band.
- Point estimates with intervals: thin ink or series-colour error bars
  (0.8 pt, no caps) or a dot with a horizontal line ("forest plot").
- Say what the band is (95 % CI, bootstrap over pairs, ±1 SD) in the
  caption — always. *(lesson: the DSH "CI" ambiguity in project 01.)*
- Paired differences get a solid ink zero line; the effect is the
  distance from it (project 01 `plot_mode_gap`).

---

## 9. Maps

EC maps are the model: trivially clean.

- Land without data: `land` gray (`#d4d4d4` on cream). Water = background.
  No satellite, no terrain shading on data maps (terrain only as a faint
  basemap for "where is" maps).
- Borders: thin white (0.4–0.6 pt) between filled regions; thin ink only
  for the one border the story is about ("Former border between East and
  West Germany").
- Classes, not gradients: 4–6 steps of a ramp, legend as a row of blocks
  with values under the seams (`stepped_legend`), placed top-left under the
  subtitle.
- Labels: a few city names in serif with a small ink dot or ring, callouts
  to highlighted regions; no full label sets.
- Hatching (thin ink diagonal lines) for a binary overlay on a choropleth
  ("Who gets to vote?").
- Point maps: dots coloured by a stepped scale, size by a second variable,
  0.4 pt edge; PNG output when there are thousands.

---

## 10. Paper checklist

- `set_style(bg="white", medium="paper")`, width from `figsize("single" |
  "onehalf" | "double")`, height by content.
- Check at 100 % of the print size: no text below 6.5 pt, lines ≥ 0.5 pt.
- No title in the image; the caption states the finding, then what is shown
  (data, n, what the band is).
- Panel letters **a**, **b** if the text refers to panels.
- Readable in grayscale: variants differ by line style, the main series is
  the darkest/thickest.
- `save_fig()` → PDF (fonts embedded as TrueType, `pdf.fonttype 42`) for
  submission, SVG to edit, PNG for Word/preview.
- Figures read only from saved CSVs; never recompute in the plotting
  function.

## 11. Web and poster checklist

- White unless the page is cream; same background for every chart on the
  page.
- Title, subtitle, source go into HTML (`<h2>`, `<figcaption>`), the chart
  is SVG and carries only axis labels and annotations.
- Alt text states the finding in one sentence.
- Phone test: at 360 px width the smallest text should still be ≥ 9 px;
  if not, a separate narrow variant (fewer labels, taller aspect).
- Posters: `compose_poster`, 4:5 portrait, cream, serif headline ≤ 5 words,
  subtitle = the finding in one sentence, footer = byline + source, PNG.
- Czech pages: decimal comma, Czech labels, `„uvozovky"`.

---

## 12. Using it in a project

```python
# src/config.py — the project's identity mapping (fixed for the whole project)
from modules.dataviz_style.chartstyle import WINE, GOLD, GREEN, VIOLET, SOLID, DASHED
METHOD_STYLE = {
    "hapax":      (WINE,   "Hapax (HL)", SOLID),
    "hapax_ind":  (WINE,   "Hapax, inductive", DASHED),
    "delta":      (GOLD,   "Cosine Delta", SOLID),
    "char_ngram": (GREEN,  "Char 2–4-grams", SOLID),
}

# src/viz.py — every chart is a function; notebooks only call it
import matplotlib.pyplot as plt
from modules.dataviz_style import chartstyle as cs

def plot_accuracy(summary, ax=None):
    cs.set_style()                        # keeps the notebook's bg/medium
    fig, ax = (ax.figure, ax) if ax else plt.subplots(figsize=cs.figsize("onehalf"))
    ...
    cs.direct_labels(ax, ends)
    return fig

# notebook
cs.set_style(bg="white", medium="paper")  # once
fig = plot_accuracy(summary)
cs.save_fig(fig, "reports/figures/accuracy")
```

Seaborn is fine for the statistics (`sns.kdeplot`, `sns.regplot`), but call
`cs.set_style()` *after* any `sns.set_theme()` (or not at all) and pass
colours explicitly.

---

## 13. Final checklist before a figure ships

- [ ] Every colour has a role, the same role as in the project's other figures.
- [ ] ≤ 4 strong hues; the rest is context gray.
- [ ] Direct labels or a sentence legend; no framed legend box.
- [ ] One annotation that says what to see (or the caption does).
- [ ] No title inside the image (unless poster).
- [ ] Fonts are Plex (not DejaVu), sizes legible at final size.
- [ ] Zero / chance / reference lines are drawn and distinguishable from data.
- [ ] Uncertainty shown and explained.
- [ ] Background matches the destination (white for papers).
- [ ] New colours passed `palette_check`.
