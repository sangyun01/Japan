"""Draw Fig. 2 of the ICEIC 2027 paper: normalized sizing sensitivity.

    python fig2_sizing_sensitivity.py

Reads the sweep CSVs next to this script and writes
results/fig2/fig2_sizing_sensitivity_{en,ko}.png and fig2_data.csv.

Each panel shows one metric divided by the baseline value, against the device
width divided by the baseline width. Noise is the sigma of a Gaussian CDF fit
to f_prob; delay and energy are arithmetic means over the 40-point DIFF grid.
"""

from pathlib import Path
import re

import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, NullLocator
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import norm


BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "results" / "fig2"
HEADER = re.compile(r"\w+_\s*\((W_[^=()]+)=([^()]+)\)\s+[XY]")

# Order fixes the color slot of each group (validated categorical palette).
GROUPS = [
    # key, baseline width (um), color, marker, English label, Korean label
    ("win", 6.4, "#2a78d6", "o", "Input pair", "입력 쌍"),
    ("tail", 3.2, "#eb6834", "s", "Tail NMOS", "Tail NMOS"),
    ("nlatch", 3.2, "#1baf7a", "^", "NMOS latch", "NMOS 래치"),
    ("platch", 1.6, "#eda100", "D", "PMOS latch", "PMOS 래치"),
    ("reset", 3.2, "#e87ba4", "v", "Reset", "리셋"),
]
TEXT = {
    "en": {
        "font": "Arial",
        "titles": ["(a) Input-referred noise", "(b) Average delay", "(c) Energy per comparison"],
        "ylabel": "Normalized to baseline",
        "xlabel": "Relative width W / W$_{\\mathrm{base}}$",
    },
    "ko": {
        "font": "Malgun Gothic",
        "titles": ["(a) 입력 환산 잡음", "(b) 평균 지연", "(c) 비교당 에너지"],
        "ylabel": "기준 회로 대비 비율",
        "xlabel": "상대 폭 W / W$_{\\mathrm{base}}$",
    },
}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e1e0d9"


def load(metric, device):
    """Return {width_um: array[[diff_V, value], ...]} sorted by DIFF."""
    data = pd.read_csv(BASE_DIR / f"{metric}_{device}_sweep.csv", encoding="utf-8-sig")
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
                "group": key, "width_um": width, "ratio": width / base,
                "sigma_uV": fit_sigma(prob[width]) * 1e6,
                "delay_avg_ns": delay[width][:, 1].mean(),
                "energy_pJ": energy[width][:, 1].mean() * 1e12,
            })
    data = pd.DataFrame(rows)
    for column in ("sigma_uV", "delay_avg_ns", "energy_pJ"):
        base = data[np.isclose(data.ratio, 1)].groupby("group")[column].first()
        data[column + "_norm"] = data[column] / data.group.map(base)
    return data


def draw(data, lang):
    text = TEXT[lang]
    plt.rcParams.update({
        "font.family": text["font"], "font.size": 8, "axes.unicode_minus": False,
        "mathtext.fontset": "custom", "mathtext.rm": text["font"],
    })
    # 7.0 in = text width of the ICEIC template, so the figure prints at 1:1 (8-pt text).
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 1.62), constrained_layout=True)
    metrics = ["sigma_uV_norm", "delay_avg_ns_norm", "energy_pJ_norm"]
    for ax, metric, title in zip(axes, metrics, text["titles"]):
        ax.axhline(1, color=MUTED, lw=0.6, zorder=1)
        ax.axvline(1, color=GRID, lw=0.6, zorder=0)
        for key, _, color, marker, label_en, label_ko in GROUPS:
            part = data[data.group == key].sort_values("ratio")
            # The baseline point is shared by every group, so it gets one neutral dot below.
            ax.plot(
                part.ratio, part[metric], color=color, lw=1.3, marker=marker, ms=4.5,
                mec="white", mew=0.8, markevery=list(np.flatnonzero(~np.isclose(part.ratio, 1))),
                label=label_en if lang == "en" else label_ko, zorder=3,
            )
        ax.plot([1], [1], marker="o", ms=4, color=INK, mec="white", mew=0.8, zorder=4)
        ax.set_xscale("log")
        ax.xaxis.set_major_locator(FixedLocator([0.5, 0.75, 1, 1.5, 2, 3]))
        ax.xaxis.set_minor_locator(NullLocator())
        ax.set_xticklabels(["0.5", "0.75", "1", "1.5", "2", "3"])
        ax.set_xlim(0.45, 3.4)
        ax.margins(y=0.12)
        ax.set_title(title, fontsize=8, loc="left", color=INK, pad=3)
        ax.grid(axis="y", color=GRID, lw=0.5)
        ax.set_axisbelow(True)
        ax.tick_params(colors=MUTED, labelcolor=INK, length=2.5, width=0.6, labelsize=7.5)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color("#c3c2b7")
            ax.spines[side].set_linewidth(0.6)
        ax.set_xlabel(text["xlabel"], fontsize=8, color=INK)
    axes[0].set_ylabel(text["ylabel"], fontsize=8, color=INK)

    # Selective direct labels: the values quoted in the text.
    def note(ax, group, ratio, metric, dx, dy, ha):
        row = data[(data.group == group) & np.isclose(data.ratio, ratio)].iloc[0]
        ax.annotate(f"{row[metric]:.2f}", (ratio, row[metric]), xytext=(dx, dy),
                    textcoords="offset points", ha=ha, va="center", fontsize=7, color=INK)

    note(axes[0], "tail", 0.5, "sigma_uV_norm", 5, -3, "left")
    note(axes[0], "nlatch", 0.5, "sigma_uV_norm", 6, 3, "left")
    note(axes[1], "platch", 3, "delay_avg_ns_norm", -6, 0, "right")
    note(axes[1], "nlatch", 0.5, "delay_avg_ns_norm", 6, 3, "left")
    note(axes[2], "platch", 3, "energy_pJ_norm", -6, 0, "right")
    note(axes[2], "tail", 0.5, "energy_pJ_norm", 5, -3, "left")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside upper center", ncol=5, frameon=False,
               fontsize=8, handlelength=2.2, columnspacing=1.6, borderaxespad=0.1)
    out = OUT_DIR / f"fig2_sizing_sensitivity_{lang}.png"
    fig.savefig(out, dpi=600, facecolor="white")
    plt.close(fig)
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = collect()
    data.to_csv(OUT_DIR / "fig2_data.csv", index=False, float_format="%.6g")
    for lang in TEXT:
        print(draw(data, lang))


if __name__ == "__main__":
    main()
