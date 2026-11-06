"""Draw the candidate formats for Fig. 2 of the ICEIC 2027 paper (sizing sensitivity).

    python fig2_sizing_sensitivity.py

Reads the sweep CSVs in data/ and writes results/fig2/fig2_data.csv and three
formats of the same numbers, in English and Korean, to results/fig2/options/:

  option1_table_*  table of the change from the baseline (%), one row per sizing change
  option2_bars_*   one panel per metric, two bars per transistor group (smaller/larger width)
  option3_lines_*  one panel per transistor group, change (%) versus the actual width,
                   with a one-line takeaway under each panel title

Noise is the sigma of a Gaussian CDF fit to f_prob; delay and energy are
arithmetic means over the 40-point DIFF grid. All three metrics are better when
lower, so a negative change is an improvement.
"""

from pathlib import Path
import re

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import norm


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "results" / "fig2"
OPT_DIR = OUT_DIR / "options"
HEADER = re.compile(r"\w+_\s*\((W_[^=()]+)=([^()]+)\)\s+[XY]")

GROUPS = [
    # key, baseline width (um), English, Korean, English short, Korean short
    ("win", 6.4, "Input pair", "입력 쌍", "Input", "입력 쌍"),
    ("tail", 3.2, "Tail NMOS", "Tail NMOS", "Tail", "Tail"),
    ("nlatch", 3.2, "NMOS latch", "NMOS 래치", "NMOS", "NMOS"),
    ("platch", 1.6, "PMOS latch", "PMOS 래치", "PMOS", "PMOS"),
    ("reset", 3.2, "Reset", "리셋", "Reset", "리셋"),
]
CANDIDATE = {"win": 8.0, "platch": 4.8}  # width used in the candidate design (um)
METRICS = ["sigma_uV", "delay_avg_ns", "energy_pJ"]
# Three series: first three slots of the validated categorical palette (all-pairs safe),
# plus marker and dash so they stay apart in grayscale print.
COLORS = {"sigma_uV": "#2a78d6", "delay_avg_ns": "#eb6834", "energy_pJ": "#1baf7a"}
MARKERS = {"sigma_uV": "o", "delay_avg_ns": "s", "energy_pJ": "^"}
DASHES = {"sigma_uV": "-", "delay_avg_ns": (0, (4, 1.5)), "energy_pJ": (0, (1.2, 1.2))}
INK, MUTED, GRID, AXIS, BAND, BAND_EDGE = "#0b0b0b", "#52514e", "#e1e0d9", "#c3c2b7", "#fbe7b0", "#c98500"
SMALL_W, LARGE_W = "#86b6ef", "#1c5cab"  # ordinal steps of one blue ramp: lighter = smaller width
UNITS = {"sigma_uV": ("µV rms", "{:.1f}"), "delay_avg_ns": ("ns", "{:.2f}"), "energy_pJ": ("pJ", "{:.1f}")}

TEXT = {
    "en": {
        "sans": "Arial", "serif": "Times New Roman",
        "metric": {"sigma_uV": "Input-referred noise", "delay_avg_ns": "Average delay",
                   "energy_pJ": "Energy per comparison"},
        "metric_short": {"sigma_uV": "Noise", "delay_avg_ns": "Avg. delay", "energy_pJ": "Energy"},
        "change": "Change from baseline (%)",
        "table_title": "TABLE I.  Change from the Baseline for Each Sizing Condition (%)",
        "table_cols": ["Group", "Width (µm)"],
        "baseline": "Baseline",
        "table_note": "Negative values are improvements; bold: |change| ≥ 10%.  ★ Width used in the candidate.",
        "bars_legend": ["Smaller width tested", "Larger width tested"],
        "band": "Width used in the candidate",
        "takeaway": {"win": "Wider: all improve", "tail": "Noise, energy ↔ delay", "nlatch": "Narrower: all worse",
                     "platch": "Wider: delay, energy ↓", "reset": "Little effect"},
        "xlabel": "W (µm)",
    },
    "ko": {
        "sans": "Malgun Gothic", "serif": "Batang",
        "metric": {"sigma_uV": "입력 환산 잡음", "delay_avg_ns": "평균 지연", "energy_pJ": "비교당 에너지"},
        "metric_short": {"sigma_uV": "잡음", "delay_avg_ns": "평균 지연", "energy_pJ": "에너지"},
        "change": "기준 회로 대비 변화 (%)",
        "table_title": "표 1. 사이징 조건별 기준 회로 대비 변화율 (%)",
        "table_cols": ["소자 그룹", "폭 (µm)"],
        "baseline": "기준 회로",
        "table_note": "음수는 개선, 굵은 값은 변화 10% 이상.  ★ candidate에 쓴 폭.",
        "bars_legend": ["작은 폭", "큰 폭"],
        "band": "candidate에 쓴 폭",
        "takeaway": {"win": "키우면 모두 소폭 개선", "tail": "잡음·에너지 ↔ 지연", "nlatch": "줄이면 모두 악화",
                     "platch": "키우면 지연·에너지↓", "reset": "영향 작음"},
        "xlabel": "W (µm)",
    },
}


def load(metric, device):
    """Return {width_um: array[[diff_V, value], ...]} sorted by DIFF."""
    data = pd.read_csv(DATA_DIR / f"{metric}_{device}_sweep.csv", encoding="utf-8-sig")
    curves = {}
    for column in range(0, data.shape[1], 2):
        width = round(float(HEADER.fullmatch(data.columns[column].strip()).group(2)) * 1e6, 4)
        values = data.iloc[:, column:column + 2].to_numpy(dtype=float)
        curves[width] = values[np.argsort(values[:, 0])]
    return curves


def fit_sigma(curve):
    x, p = curve.T
    (mu, sigma), _ = curve_fit(
        lambda v, m, s: norm.cdf(v, loc=m, scale=s), x, p,
        p0=[0.0, 2e-4], bounds=([-np.inf, 1e-12], [np.inf, np.inf]),
    )
    return sigma


def collect():
    rows = []
    for key, base, *_ in GROUPS:
        prob, delay, energy = (load(m, key) for m in ("f_prob", "f_delay_avg", "E_comp"))
        for width in sorted(prob):
            rows.append({
                "group": key, "base_um": base, "width_um": width,
                "sigma_uV": fit_sigma(prob[width]) * 1e6,
                "delay_avg_ns": delay[width][:, 1].mean(),
                "energy_pJ": energy[width][:, 1].mean() * 1e12,
            })
    data = pd.DataFrame(rows)
    data["is_base"] = np.isclose(data.width_um, data.base_um)
    for column in METRICS:
        base = data[data.is_base].groupby("group")[column].first()
        data[column + "_pct"] = 100 * (data[column] / data.group.map(base) - 1)
    return data


def wtext(w):
    return f"{w:.2f}".rstrip("0") if abs(w - round(w, 1)) > 1e-6 else f"{w:.1f}"


def signed(v, digits):
    text = f"{v:+.{digits}f}"
    return "0" if float(text) == 0 else text.replace("-", "−")


def is_candidate(r):
    return CANDIDATE.get(r.group) == round(r.width_um, 1)


def style_axis(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
        ax.spines[side].set_linewidth(0.6)
    ax.tick_params(colors=AXIS, labelcolor=INK, length=2.5, width=0.6, labelsize=8)
    ax.grid(axis="y", color=GRID, lw=0.5)
    ax.set_axisbelow(True)


def save(fig, name):
    out = OPT_DIR / name
    fig.savefig(out, dpi=600, facecolor="white")
    plt.close(fig)
    return out


def draw_table(data, lang):
    """Option 1: paper-style table (serif, horizontal rules), rendered as a preview image."""
    t = TEXT[lang]
    plt.rcParams.update({"font.family": ["Times New Roman", t["serif"], "Segoe UI Symbol"], "font.size": 8})
    rows = [(t["baseline"], None)]
    for key, base, name_en, name_ko, *_ in GROUPS:
        part = data[(data.group == key) & ~data.is_base].sort_values("width_um")
        for n, (_, r) in enumerate(part.iterrows()):
            rows.append(((name_en if lang == "en" else name_ko) if n == 0 else "", r))
    width, line, top = 4.6, 0.155, 0.4
    height = top + line * (len(rows) + 1) + 0.32
    fig = plt.figure(figsize=(width, height))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")
    left, right = 0.05, width - 0.05
    x_group, x_width, x_cols = 0.1, 2.0, [2.95, 3.78, 4.5]
    ax.text(width / 2, 0.2, t["table_title"], ha="center", va="center", fontsize=8, color=INK)

    y = top
    ax.plot([left, right], [y, y], color=INK, lw=0.8)
    y += line * 0.55
    ax.text(x_group, y, t["table_cols"][0], ha="left", va="center", fontsize=8, fontweight="bold")
    ax.text(x_width, y, t["table_cols"][1], ha="right", va="center", fontsize=8, fontweight="bold")
    for x, m in zip(x_cols, METRICS):
        ax.text(x, y, t["metric_short"][m], ha="right", va="center", fontsize=8, fontweight="bold")
    y += line * 0.55
    ax.plot([left, right], [y, y], color=INK, lw=0.5)
    y -= line / 2

    base_row = data[data.is_base].iloc[0]
    prev_group = None
    for label, r in rows:
        y += line
        if r is None:
            ax.text(x_group, y, label, ha="left", va="center", fontsize=8)
            ax.text(x_width, y, "—    ", ha="right", va="center", fontsize=8)
            for x, m in zip(x_cols, METRICS):
                unit, fmt = UNITS[m]
                ax.text(x, y, fmt.format(base_row[m]) + " " + unit, ha="right", va="center", fontsize=8)
            continue
        if r.group != prev_group:
            ax.plot([left, right], [y - line / 2, y - line / 2], color=AXIS, lw=0.5)
            prev_group = r.group
        cand = is_candidate(r)
        if cand:
            ax.add_patch(Rectangle((left, y - line / 2), right - left, line, color=BAND, lw=0, zorder=0))
        ax.text(x_group, y, label, ha="left", va="center", fontsize=8)
        ax.text(x_width, y, f"{wtext(r.base_um)} → {wtext(r.width_um)}" + (" ★" if cand else "    "),
                ha="right", va="center", fontsize=8)
        for x, m in zip(x_cols, METRICS):
            v = r[m + "_pct"]
            ax.text(x, y, signed(v, 1), ha="right", va="center", fontsize=8,
                    fontweight="bold" if abs(v) >= 10 else "normal")
    y += line / 2
    ax.plot([left, right], [y, y], color=INK, lw=0.8)
    ax.text(left, y + 0.17, t["table_note"], ha="left", va="center", fontsize=8, color=MUTED)
    return save(fig, f"option1_table_{lang}.png")


def draw_bars(data, lang):
    """Option 2: one panel per metric; per group, a bar for the smaller and the larger width tested."""
    t = TEXT[lang]
    plt.rcParams.update({"font.family": [t["sans"], "Arial"], "font.size": 8, "axes.unicode_minus": True})
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.25), sharey=True, constrained_layout=True)
    fig.get_layout_engine().set(w_pad=0.03, wspace=0.03)
    xs = np.arange(len(GROUPS))
    for ax, m in zip(axes, METRICS):
        ax.axhline(0, color=MUTED, lw=0.8, zorder=2)
        ticklabels = []
        for x, (key, base, _, _, short_en, short_ko) in zip(xs, GROUPS):
            part = data[(data.group == key) & ~data.is_base].sort_values("width_um")
            pair = part[m + "_pct"].to_numpy()
            for i, (dx, color, (_, r)) in enumerate(zip((-0.21, 0.21), (SMALL_W, LARGE_W), part.iterrows())):
                v = r[m + "_pct"]
                ax.bar(x + dx, v, width=0.42, color=color, zorder=3, lw=0)
                if is_candidate(r):
                    ax.bar(x + dx, v, width=0.42, fill=False, edgecolor=BAND_EDGE, lw=1.4, zorder=4)
                # Label changes of 10% or more and the candidate bars; small changes are read from the bar.
                if abs(v) < 10 and not is_candidate(r):
                    continue
                if i == 0 and np.sign(pair[1]) == np.sign(v) and abs(pair[1]) > abs(v):
                    # The longer right-hand bar would cover a label under this one: put it to the left.
                    ax.text(x + dx - 0.24, v, signed(v, 0), ha="right", va="center", fontsize=8, color=INK, zorder=5)
                else:
                    ax.text(x + dx, v + (1.5 if v >= 0 else -1.5), signed(v, 0), ha="center",
                            va="bottom" if v >= 0 else "top", fontsize=8, color=INK, zorder=5)
            ticklabels.append(f"{short_en if lang == 'en' else short_ko}\n"
                              f"{wtext(part.width_um.iloc[0])}/{wtext(part.width_um.iloc[1])}")
        ax.set_xticks(xs)
        ax.set_xticklabels(ticklabels, fontsize=8, linespacing=1.15)
        ax.set_xlim(-0.6, len(GROUPS) - 0.4)
        ax.set_title(t["metric"][m], fontsize=8, color=INK, pad=3)
        style_axis(ax)
        ax.tick_params(axis="x", length=0)
    axes[0].set_ylim(-62, 36)
    axes[0].set_yticks([-50, -25, 0, 25])
    axes[0].set_ylabel(t["change"], fontsize=8, color=INK)
    handles = [Patch(color=SMALL_W), Patch(color=LARGE_W), Patch(facecolor="white", edgecolor=BAND_EDGE, lw=1.4)]
    fig.legend(handles, [*t["bars_legend"], t["band"]], loc="outside upper center", ncol=3, frameon=False,
               fontsize=8, columnspacing=1.8)
    return save(fig, f"option2_bars_{lang}.png")


def draw_lines(data, lang):
    """Option 3: one panel per group, change (%) versus the actual width, with a takeaway line."""
    t = TEXT[lang]
    plt.rcParams.update({"font.family": [t["sans"], "Arial", "Segoe UI Symbol"], "font.size": 8,
                         "axes.unicode_minus": True})
    fig, axes = plt.subplots(1, 5, figsize=(7.0, 2.2), sharey=True, constrained_layout=True)
    fig.get_layout_engine().set(w_pad=0.02, wspace=0.04)
    # Values quoted in the text: (group, metric) -> (end of sweep, dx, dy) in points.
    notes = {("tail", "sigma_uV"): (0, 0, -9), ("nlatch", "delay_avg_ns"): (0, 5, 3),
             ("platch", "delay_avg_ns"): (-1, 5, 0), ("platch", "energy_pJ"): (-1, 5, 0)}
    for n, (ax, (key, base, name_en, name_ko, *_)) in enumerate(zip(axes, GROUPS)):
        part = data[data.group == key].sort_values("width_um")
        widths = part.width_um.to_numpy()
        pad = 0.25 * (widths[-1] - widths[0])
        ax.set_xlim(widths[0] - pad, widths[-1] + pad)
        if key in CANDIDATE:
            ax.axvspan(CANDIDATE[key] - pad * 0.3, CANDIDATE[key] + pad * 0.3, color=BAND, lw=0, zorder=0)
        ax.axhline(0, color=MUTED, lw=0.6, zorder=1)
        ax.axvline(base, color=AXIS, lw=0.6, zorder=1)
        for m in METRICS:
            ax.plot(widths, part[m + "_pct"], color=COLORS[m], marker=MARKERS[m], ms=4.5, lw=1.4,
                    linestyle=DASHES[m], mec="white", mew=0.7, zorder=3)
            if (key, m) in notes:
                end, dx, dy = notes[(key, m)]
                v = part[m + "_pct"].iloc[end]
                ax.annotate(signed(v, 0) + "%", (widths[end], v), xytext=(dx, dy), textcoords="offset points",
                            ha="left" if dx > 0 else "center", va="center", fontsize=8, color=INK, zorder=4)
        ax.set_xticks(widths)
        ax.set_xticklabels([wtext(w) for w in widths])
        for tick, w in zip(ax.get_xticklabels(), widths):
            if np.isclose(w, base):
                tick.set_fontweight("bold")
        name = name_en if lang == "en" else name_ko
        ax.set_title(f"({'abcde'[n]}) {name}\n", fontsize=8, color=INK, pad=2, linespacing=1.3)
        ax.text(0.5, 1.03, t["takeaway"][key], transform=ax.transAxes, ha="center", va="bottom",
                fontsize=8, color=MUTED)
        ax.set_xlabel(t["xlabel"], fontsize=8, color=MUTED, labelpad=1)
        style_axis(ax)
    axes[0].set_ylim(-58, 35)
    axes[0].set_yticks([-50, -25, 0, 25])
    axes[0].set_ylabel(t["change"], fontsize=8, color=INK)
    handles = [Line2D([], [], color=COLORS[m], marker=MARKERS[m], ms=4.5, lw=1.4, linestyle=DASHES[m],
                      mec="white", mew=0.7) for m in METRICS]
    handles.append(Patch(color=BAND, lw=0))
    fig.legend(handles, [*(t["metric"][m] for m in METRICS), t["band"]], loc="outside upper center", ncol=4,
               frameon=False, fontsize=8, handlelength=2.4, columnspacing=1.6)
    return save(fig, f"option3_lines_{lang}.png")


def main():
    OPT_DIR.mkdir(parents=True, exist_ok=True)
    data = collect()
    data.to_csv(OUT_DIR / "fig2_data.csv", index=False, float_format="%.6g")
    for lang in TEXT:
        for draw in (draw_table, draw_bars, draw_lines):
            print(draw(data, lang))


if __name__ == "__main__":
    main()
