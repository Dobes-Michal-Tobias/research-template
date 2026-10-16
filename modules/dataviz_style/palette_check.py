"""Computable checks for chart palettes — validate by computation, not by eye.

Python port of the dataviz skill's `validate_palette.js` (same thresholds,
Machado et al. 2009 CVD simulation, OKLab distances), extended with a check
for sequential ramps (lightness must change monotonically).

    python -m modules.dataviz_style.palette_check                 # every named palette, both surfaces
    python -m modules.dataviz_style.palette_check "#a61b57,#b07d00" "#ffffff"

Categorical checks: lightness band, chroma floor, CVD separation (protan /
deutan), normal-vision floor, contrast against the chart surface.
Sequential checks: monotonic OKLCH lightness, minimum step between neighbours.
"""

from __future__ import annotations

import math
import sys

BAND = (0.43, 0.77)          # OKLCH L for line/dot marks on a light surface
CHROMA_FLOOR = 0.10          # OKLCH C
CVD_TARGET, CVD_FLOOR = 8.0, 6.0
NORMAL_FLOOR = 15.0
CONTRAST_MIN = 3.0
SEQ_STEP_MIN = 0.04          # OKLCH L between neighbouring ramp steps

MACHADO = {
    "protan": [[0.152286, 1.052583, -0.204868],
               [0.114503, 0.786281, 0.099216],
               [-0.003882, -0.048116, 1.051998]],
    "deutan": [[0.367322, 0.860646, -0.227968],
               [0.280085, 0.672501, 0.047413],
               [-0.011820, 0.042940, 0.968881]],
    "tritan": [[1.255528, -0.076749, -0.178779],
               [-0.078411, 0.930809, 0.147602],
               [0.004733, 0.691367, 0.303900]],
}


def _lin(hex_color: str) -> list[float]:
    h = hex_color.strip().lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return out


def _cbrt(x: float) -> float:
    return math.copysign(abs(x) ** (1 / 3), x)


def _oklab(rgb_lin: list[float]) -> tuple[float, float, float]:
    r, g, b = rgb_lin
    l = _cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = _cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = _cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )


def _simulate(hex_color: str, kind: str) -> list[float]:
    r, g, b = _lin(hex_color)
    M = MACHADO[kind]
    return [min(1.0, max(0.0, M[i][0] * r + M[i][1] * g + M[i][2] * b)) for i in range(3)]


def oklch(hex_color: str) -> tuple[float, float]:
    """(lightness, chroma) in OKLCH."""
    L, a, b = _oklab(_lin(hex_color))
    return L, math.hypot(a, b)


def delta_e(h1: str, h2: str, kind: str | None = None) -> float:
    """OKLab distance ×100, optionally after simulating a colour-vision deficiency."""
    a = _oklab(_simulate(h1, kind) if kind else _lin(h1))
    b = _oklab(_simulate(h2, kind) if kind else _lin(h2))
    return 100 * math.dist(a, b)


def contrast(h1: str, h2: str) -> float:
    """WCAG contrast ratio."""
    def lum(h):
        r, g, b = _lin(h)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    hi, lo = sorted([lum(h1), lum(h2)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def validate(palette: list[str], surface: str, pairs: str = "adjacent", band: tuple[float, float] = BAND,
             chroma_floor: float = CHROMA_FLOOR) -> tuple[list[tuple[str, str, str]], bool]:
    """Categorical palette checks. Returns ([(check, PASS|WARN|FAIL, detail)], ok).

    Fill palettes (bars, areas) may pass a wider `band` and lower
    `chroma_floor`; they then rely on direct labels in darker text twins.
    """
    report, ok = [], True
    lo, hi = band

    off = [(c, round(oklch(c)[0], 3)) for c in palette if not lo <= oklch(c)[0] <= hi]
    ok &= not off
    report.append(("Lightness band", "FAIL" if off else "PASS", f"outside: {off}" if off else f"all in L {lo}-{hi}"))

    lowc = [(c, round(oklch(c)[1], 3)) for c in palette if oklch(c)[1] < chroma_floor]
    ok &= not lowc
    report.append(("Chroma floor", "FAIL" if lowc else "PASS", f"below: {lowc}" if lowc else f"all >= {chroma_floor}"))

    n = len(palette)
    pairlist = ([(i, j) for i in range(n) for j in range(i + 1, n)] if pairs == "all"
                else [(i, i + 1) for i in range(n - 1)])
    worst = min(((delta_e(palette[i], palette[j], k), k, palette[i], palette[j])
                 for k in ("protan", "deutan") for i, j in pairlist), default=(99, "", "", ""))
    state = "PASS" if worst[0] >= CVD_TARGET else "WARN" if worst[0] >= CVD_FLOOR else "FAIL"
    ok &= state != "FAIL"
    report.append(("CVD separation", state, f"worst {pairs} {worst[2]}<->{worst[3]} dE {worst[0]:.1f} ({worst[1]})"))

    nworst = min(((delta_e(palette[i], palette[j]), palette[i], palette[j]) for i, j in pairlist), default=(99, "", ""))
    state = "PASS" if nworst[0] >= NORMAL_FLOOR else "FAIL"
    ok &= state != "FAIL"
    report.append(("Normal-vision floor", state, f"worst {nworst[1]}<->{nworst[2]} dE {nworst[0]:.1f}"))

    low = [(c, round(contrast(c, surface), 2)) for c in palette if contrast(c, surface) < CONTRAST_MIN]
    report.append(("Contrast vs surface", "WARN" if low else "PASS",
                   f"below 3:1 (needs direct labels/table): {low}" if low else "all >= 3:1"))
    return report, ok


def validate_sequential(ramp: list[str]) -> tuple[list[tuple[str, str, str]], bool]:
    """Sequential ramp checks: lightness strictly monotonic with a minimum step."""
    Ls = [oklch(c)[0] for c in ramp]
    diffs = [b - a for a, b in zip(Ls, Ls[1:])]
    mono = all(d < 0 for d in diffs) or all(d > 0 for d in diffs)
    step = min(abs(d) for d in diffs)
    report = [
        ("Monotonic lightness", "PASS" if mono else "FAIL", " -> ".join(f"{L:.2f}" for L in Ls)),
        ("Minimum step", "PASS" if step >= SEQ_STEP_MIN else "WARN", f"smallest dL {step:.3f} (target >= {SEQ_STEP_MIN})"),
    ]
    return report, mono


def validate_diverging(ramp: list[str]) -> tuple[list[tuple[str, str, str]], bool]:
    """Diverging ramp: each arm monotonic towards the light midpoint, and every mirrored
    pair of steps (same distance from the midpoint, so similar lightness) still
    distinguishable under protan/deutan simulation — the sign must not vanish for CVD readers."""
    mid = len(ramp) // 2
    rep_l, ok_l = validate_sequential(ramp[:mid + 1])
    rep_r, ok_r = validate_sequential(ramp[mid:][::-1])
    mirror = [min(delta_e(ramp[i], ramp[-1 - i], k) for k in ("protan", "deutan")) for i in range(mid)]
    worst = min(mirror)
    state = "PASS" if worst >= CVD_TARGET else "WARN" if worst >= CVD_FLOOR else "FAIL"
    report = [("Left arm " + r[0], r[1], r[2]) for r in rep_l] + [("Right arm " + r[0], r[1], r[2]) for r in rep_r]
    report.append(("Mirrored steps CVD", state, "dE " + ", ".join(f"{d:.1f}" for d in mirror)))
    return report, ok_l and ok_r and state != "FAIL"


def _print(title: str, report: list[tuple[str, str, str]], ok: bool) -> None:
    print(title)
    for name, state, detail in report:
        print(f"  [{state:4}] {name:28} {detail}")
    print("  ->", "ALL CHECKS PASS" if ok else "FAILED")


def print_report(palette: list[str], surface: str, pairs: str = "adjacent",
                 band: tuple[float, float] = BAND) -> bool:
    report, ok = validate(palette, surface, pairs, band)
    _print(f"Palette ({len(palette)} slots, surface {surface}, pairs={pairs})", report, ok)
    return ok


def check_all() -> bool:
    """Validate every palette declared in chartstyle on both surfaces."""
    from modules.dataviz_style import chartstyle as cs

    all_ok = True
    for name, spec in cs.CATEGORICAL.items():
        band, chroma = spec.get("band", BAND), spec.get("chroma", CHROMA_FLOOR)
        for bg in ("white", "cream"):
            report, ok = validate(spec["colors"], cs.SURFACES[bg]["bg"], "all", band, chroma)
            _print(f"\n{name} on {bg} ({spec['use']})", report, ok)
            all_ok &= ok
    for name, ramp in cs.SEQUENTIAL.items():
        report, ok = validate_sequential(ramp)
        _print(f"\nsequential {name}", report, ok)
        all_ok &= ok
    for name, ramp in cs.DIVERGING.items():
        report, ok = validate_diverging(ramp)
        _print(f"\ndiverging {name}", report, ok)
        all_ok &= ok
    print("\n==>", "EVERY PALETTE PASSES" if all_ok else "SOME PALETTES FAILED")
    return all_ok


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pal = [c.strip() for c in sys.argv[1].split(",") if c.strip()]
        surf = sys.argv[2] if len(sys.argv) > 2 else "#ffffff"
        sys.exit(0 if print_report(pal, surf, "all") else 1)
    sys.exit(0 if check_all() else 1)
