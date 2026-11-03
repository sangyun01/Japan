"""Fit probability and plot every sampled DIFF value in a candidate/baseline CSV.

Run from the project root after conda activate aiot:
    python sim_result/candidate_analysis.py
    python sim_result/candidate_analysis.py --no-show
    python sim_result/candidate_analysis.py --input sim_result/data/baseline.csv --no-show

DIFF is stored in V and plotted in mV. Other metrics retain CSV units.
Average/maximum delays share an axis; Energy and E_comp use separate axes.
Outputs: four individual PNGs, a 2x2 overview, and a CDF fit summary CSV.
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from f_prob_analysis import gaussian_cdf


BASE_DIR = Path(__file__).resolve().parent
METRICS = ("Energy", "f_prob", "f_delay_avg", "f_delay_max", "E_comp")
PANELS = ("f_prob_cdf_fit", "delay_vs_diff", "energy_vs_diff", "e_comp_vs_diff")
COLORS = ("#2769b3", "#db6c24")


def load_data(path):
    data = pd.read_csv(path)
    expected = {f"{metric} {axis}" for metric in METRICS for axis in ("X", "Y")}
    if set(data.columns) != expected or data.empty:
        raise ValueError("Expected nonempty Energy/f_prob/f_delay_avg/f_delay_max/E_comp X/Y pairs")
    curves = {}
    for metric in METRICS:
        values = data[[f"{metric} X", f"{metric} Y"]].to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise ValueError(f"{metric}: nonfinite or missing data")
        values = values[np.argsort(values[:, 0])]
        if len(values) < 3 or np.any(np.diff(values[:, 0]) <= 0):
            raise ValueError(f"{metric}: expected at least three distinct DIFF samples")
        curves[metric] = values
    reference = curves["f_prob"][:, 0]
    if any(not np.allclose(values[:, 0], reference, rtol=0, atol=1e-12)
           for values in curves.values()):
        raise ValueError("Metrics have different DIFF grids")
    probability = curves["f_prob"][:, 1]
    if np.any((probability < 0) | (probability > 1)):
        raise ValueError("f_prob must lie between 0 and 1")
    if not probability.min() < 0.5 < probability.max():
        raise ValueError("f_prob must span the 0.5 transition")
    if np.count_nonzero((probability > 0) & (probability < 1)) < 2:
        raise ValueError("Insufficient transition samples to estimate sigma")
    return curves


def fit_probability(curve):
    # Same model, initial values and positive-sigma constraint as cdf_fit.py.
    x, probability = curve.T
    parameters, _ = curve_fit(
        gaussian_cdf, x, probability,
        p0=[0, 100e-6],
        bounds=([-np.inf, 1e-12], [np.inf, np.inf]),
        maxfev=10000,
    )
    mu, sigma = parameters
    if not np.isfinite(parameters).all() or sigma <= 0:
        raise ValueError("CDF fit returned invalid mu or sigma")
    rmse = np.sqrt(np.mean((probability - gaussian_cdf(x, mu, sigma)) ** 2))
    return float(mu), float(sigma), float(rmse)


def draw_panel(ax, panel, curves, fit):
    if panel == "f_prob_cdf_fit":
        x, probability = curves["f_prob"].T
        mu, sigma, _ = fit
        x_fit = np.linspace(x.min(), x.max(), 600)
        ax.scatter(x * 1e3, probability, color=COLORS[0], s=22,
                   label=f"Simulation ({len(x)} points)", zorder=3)
        ax.plot(x_fit * 1e3, gaussian_cdf(x_fit, mu, sigma),
                color=COLORS[1], linewidth=1.8, label="Gaussian CDF fit")
        ax.text(0.04, 0.96,
                f"$\\mu$ = {mu * 1e6:.2f} $\\mu$V\n"
                f"$\\sigma$ = {sigma * 1e6:.2f} $\\mu$V RMS",
                transform=ax.transAxes, va="top", fontsize=10,
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.85))
        ax.set_title("f_prob: Gaussian CDF fit")
        ax.set_ylabel("Probability")
        ax.set_ylim(-0.03, 1.03)
        ax.legend(loc="lower right")
    else:
        metrics, title, ylabel = {
            "delay_vs_diff": (("f_delay_avg", "f_delay_max"),
                              "Average and maximum delay", "Delay (CSV units)"),
            "energy_vs_diff": (("Energy",), "Energy", "Energy (CSV units)"),
            "e_comp_vs_diff": (("E_comp",), "Energy per comparison", "E_comp (CSV units)"),
        }[panel]
        for index, metric in enumerate(metrics):
            x, y = curves[metric].T
            ax.plot(x * 1e3, y, marker=("o", "s")[index], markersize=3.5,
                    linewidth=1.4, color=COLORS[index], label=metric)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        if panel != "delay_vs_diff":
            ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0), useOffset=False)
        ax.legend(loc="best")
    diff = curves["f_prob"][:, 0] * 1e3
    ax.set_xlim(diff.min(), diff.max())
    ax.set_xticks(np.linspace(diff.min(), diff.max(), 7))
    ax.set_xlabel("DIFF (mV)")
    ax.grid(True, alpha=0.25)
    ax.set_axisbelow(True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", type=Path, default=BASE_DIR / "data" / "cadidate.csv")
    parser.add_argument("--output-dir", type=Path, help="Default: results/<input stem>")
    parser.add_argument("--no-show", action="store_true", help="Save plots without opening windows")
    args = parser.parse_args()
    dataset = "candidate" if args.input.stem == "cadidate" else args.input.stem
    if args.output_dir is None:
        args.output_dir = BASE_DIR / "results" / dataset
    if args.no_show:
        plt.switch_backend("Agg")
    try:
        curves = load_data(args.input)
        fit = fit_probability(curves["f_prob"])
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"Analysis error: {exc}\n")

    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    args.output_dir.mkdir(parents=True, exist_ok=True)
    figures = []
    for panel in PANELS:
        fig, ax = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
        draw_panel(ax, panel, curves, fit)
        fig.savefig(args.output_dir / f"{panel}.png", dpi=200, facecolor="white")
        figures.append(fig)
    overview, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    for ax, panel in zip(axes.flat, PANELS):
        draw_panel(ax, panel, curves, fit)
    overview.suptitle(f"{dataset.replace('_', ' ').title()}: DIFF sweep (all {len(curves['f_prob'])} samples)")
    overview.savefig(args.output_dir / f"{dataset}_overview.png", dpi=200, facecolor="white")
    figures.append(overview)

    mu, sigma, rmse = fit
    summary = pd.DataFrame([{
        "source_file": args.input.name,
        "points": len(curves["f_prob"]),
        "mu_uV": mu * 1e6,
        "sigma_uV_rms": sigma * 1e6,
        "noise_variance_mV2": (sigma * 1e3) ** 2,
        "rmse_probability": rmse,
    }])
    summary.to_csv(args.output_dir / f"{dataset}_cdf_summary.csv", index=False, encoding="utf-8-sig")
    print(summary.to_string(index=False, float_format=lambda value: f"{value:.8g}"))
    print("All sampled DIFF points plotted; X: V -> mV; other metrics retain CSV units.")
    print(f"Results saved to: {args.output_dir.resolve()}")
    if not args.no_show:
        plt.show()
    for fig in figures:
        plt.close(fig)


if __name__ == "__main__":
    main()
