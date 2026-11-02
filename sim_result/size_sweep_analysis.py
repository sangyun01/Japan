"""Summarize energy and delay changes with transistor width.

Run in the aiot environment:
    python size_sweep_analysis.py
    python size_sweep_analysis.py --device win platch --no-show

The three metric summaries are arithmetic means over the sampled DIFF grid.
The peak of f_delay_max over that grid is also saved separately.
All metric values retain their original CSV units. Width is reported in um.
Percent changes use the smallest width of each device as the reference.
"""

import argparse
from pathlib import Path
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DEVICES = {
    "win": "W_in_M79", "nlatch": "W_nlatch_M68", "reset": "W_resetXY_M14",
    "platch": "W_platch_M23", "tail": "W_tail_M10",
}
METRICS = ("E_comp", "f_delay_avg", "f_delay_max")
HEADER = re.compile(
    r"(?P<metric>E_comp|f_delay_avg|f_delay_max)_\s*"
    r"\((?P<parameter>W_[^=()]+)=(?P<width>[^()]+)\)\s+(?P<axis>[XY])"
)


def load_metric(path, device, metric):
    """Read and validate all width curves, independently of column order."""
    data = pd.read_csv(path)
    if data.empty or len(data.columns) % 2:
        raise ValueError(f"{path.name}: expected nonempty X/Y column pairs")
    curves = {}
    for column in range(0, len(data.columns), 2):
        headers = [HEADER.fullmatch(str(name).strip()) for name in data.columns[column:column + 2]]
        if any(header is None for header in headers):
            raise ValueError(f"{path.name}: invalid headers at column {column + 1}")
        x_info, y_info = [header.groupdict() for header in headers]
        if (
            x_info["axis"] != "X" or y_info["axis"] != "Y"
            or any(x_info[key] != y_info[key] for key in ("metric", "parameter", "width"))
            or x_info["metric"] != metric or x_info["parameter"] != DEVICES[device]
        ):
            raise ValueError(f"{path.name}: mismatched X/Y headers")
        width = float(x_info["width"])
        values = data.iloc[:, column:column + 2].to_numpy(dtype=float)
        if not np.isfinite(width) or width <= 0 or not np.isfinite(values).all():
            raise ValueError(f"{path.name}: nonfinite data or invalid width")
        values = values[np.argsort(values[:, 0])]
        if len(values) < 2 or np.any(np.diff(values[:, 0]) <= 0) or width in curves:
            raise ValueError(f"{path.name}: duplicate widths or invalid DIFF grid")
        curves[width] = values
    return curves


def direction(values):
    changes = np.diff(np.asarray(values) / values[0])
    tolerance = 1e-8
    if np.all(np.abs(changes) <= tolerance):
        return "unchanged"
    if np.all(changes >= -tolerance):
        return "increases"
    if np.all(changes <= tolerance):
        return "decreases"
    return "nonmonotonic"


def summarize_device(device, input_dir):
    curves = {
        metric: load_metric(input_dir / f"{metric}_{device}_sweep.csv", device, metric)
        for metric in METRICS
    }
    widths = sorted(curves[METRICS[0]])
    if any(set(curves[metric]) != set(widths) for metric in METRICS):
        raise ValueError(f"{device}: metric files have different width sets")
    reference_x = curves[METRICS[0]][widths[0]][:, 0]
    rows = []
    for width in widths:
        row = {
            "device": device, "parameter": DEVICES[device], "width_um": width * 1e6,
            "points": len(reference_x), "diff_min_mV": reference_x[0] * 1e3,
            "diff_max_mV": reference_x[-1] * 1e3,
        }
        for metric in METRICS:
            values = curves[metric][width]
            if values.shape[0] != len(reference_x) or not np.allclose(
                values[:, 0], reference_x, rtol=0, atol=1e-12
            ):
                raise ValueError(f"{device}: DIFF grids do not match across widths and metrics")
            row[f"{metric}_mean_over_diff"] = values[:, 1].mean()
        row["f_delay_max_peak_over_diff"] = curves["f_delay_max"][width][:, 1].max()
        rows.append(row)

    table = pd.DataFrame(rows)
    trend = {
        "device": device, "width_min_um": widths[0] * 1e6,
        "width_max_um": widths[-1] * 1e6,
    }
    value_columns = [f"{metric}_mean_over_diff" for metric in METRICS] + ["f_delay_max_peak_over_diff"]
    for column in value_columns:
        values = table[column].to_numpy()
        if values[0] <= 0:
            raise ValueError(f"{device}: expected positive reference for {column}")
        table[f"{column}_change_pct"] = (values / values[0] - 1) * 100
        trend[f"{column}_change_pct"] = table[f"{column}_change_pct"].iloc[-1]
        trend[f"{column}_direction"] = direction(values)
    return table, trend


def plot_summary(summary):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    for ax, metric in zip(axes, METRICS):
        for device, table in summary.groupby("device", sort=False):
            ax.plot(
                table["width_um"], table[f"{metric}_mean_over_diff_change_pct"],
                "o-", label=device, markersize=5,
            )
        ax.axhline(0, color="gray", linewidth=0.7)
        ax.set_title(f"{metric}: mean over DIFF")
        ax.set_xlabel("Transistor width (um)")
        ax.set_ylabel("Change from smallest width (%)")
        ax.grid(True, alpha=0.3)
        ax.legend()
    fig.suptitle("Size sweep: energy and delay trends")
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--device", nargs="+", choices=list(DEVICES), default=list(DEVICES))
    parser.add_argument("--input-dir", type=Path, default=BASE_DIR)
    parser.add_argument("--output-dir", type=Path, default=BASE_DIR / "results" / "size_sweep")
    parser.add_argument("--no-show", action="store_true")
    args = parser.parse_args()
    tables, trends = [], []
    try:
        for device in dict.fromkeys(args.device):
            table, trend = summarize_device(device, args.input_dir)
            tables.append(table)
            trends.append(trend)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Analysis error: {exc}\n")
    summary = pd.concat(tables, ignore_index=True)
    trend_summary = pd.DataFrame(trends)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output_dir / "size_sweep_summary.csv", index=False, encoding="utf-8-sig")
    trend_summary.to_csv(args.output_dir / "size_sweep_trends.csv", index=False, encoding="utf-8-sig")
    fig = plot_summary(summary)
    fig.savefig(args.output_dir / "size_sweep_trends.png", dpi=200)
    print("Values retain CSV units. Each mean is the arithmetic mean over the shared DIFF grid.")
    print("Percent change compares each device's smallest width to its largest width.")
    print("f_delay_max_mean_over_diff averages the per-DIFF maxima; peak_over_diff is the overall observed maximum.")
    print(summary.iloc[:, :10].to_string(index=False, float_format=lambda value: f"{value:.6g}"))
    print("\nTrends:")
    print(trend_summary.to_string(index=False, float_format=lambda value: f"{value:.3f}"))
    print(f"\nResults saved to: {args.output_dir.resolve()}")
    print("Output files are replaced on each run with the selected devices.")
    if not args.no_show:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    main()
