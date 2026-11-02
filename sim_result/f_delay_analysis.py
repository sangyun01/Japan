"""Compare f_delay sweeps using the load / summarize / plot flow of cdf_fit.py.

Run all devices:
    python f_delay_analysis.py
Run a selected device and label the original delay values in ns:
    python f_delay_analysis.py --device win --delay-unit ns
Save figures without opening windows:
    python f_delay_analysis.py --no-show

X values are converted from V to mV; widths are converted from m to um.
Delay values keep their CSV scale. --delay-unit only sets the label.
Gaussian CDF fitting is for probability data, so no CDF fit is applied here.
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DEVICES = {
    "win": "W_in_M79",
    "nlatch": "W_nlatch_M68",
    "reset": "W_resetXY_M14",
    "platch": "W_platch_M23",
    "tail": "W_tail_M10",
}
METRICS = {"avg": "Average delay", "max": "Maximum delay"}
HEADER = re.compile(
    r"f_delay_(?P<metric>avg|max)_\s*"
    r"\((?P<parameter>W_[^=()]+)=(?P<width>[^()]+)\)\s+(?P<axis>[XY])"
)


@dataclass
class SweepCurve:
    width_m: float
    x_v: np.ndarray
    delay: np.ndarray


# 1. CSV 파일 불러오기: 각 사이즈의 X/Y 열 쌍을 모두 읽는다.
def load_sweep(path, device, metric):
    data = pd.read_csv(path)
    if data.empty or len(data.columns) % 2:
        raise ValueError(f"{path.name}: expected nonempty X/Y column pairs")

    curves = []
    for column in range(0, len(data.columns), 2):
        x_header = HEADER.fullmatch(data.columns[column].strip())
        y_header = HEADER.fullmatch(data.columns[column + 1].strip())
        if x_header is None or y_header is None:
            raise ValueError(f"{path.name}: unsupported header at column {column + 1}")

        x_info, y_info = x_header.groupdict(), y_header.groupdict()
        if (
            x_info["axis"] != "X"
            or y_info["axis"] != "Y"
            or any(x_info[key] != y_info[key] for key in ("metric", "parameter", "width"))
            or x_info["metric"] != metric
            or x_info["parameter"] != DEVICES[device]
        ):
            raise ValueError(f"{path.name}: mismatched X/Y headers at column {column + 1}")

        width = float(x_info["width"])
        values = data.iloc[:, column : column + 2].to_numpy(dtype=float)
        if not np.isfinite(width) or width <= 0 or not np.isfinite(values).all():
            raise ValueError(f"{path.name}: nonfinite data or invalid width")
        values = values[np.argsort(values[:, 0])]
        if len(values) < 2 or np.any(np.diff(values[:, 0]) <= 0):
            raise ValueError(f"{path.name}: expected at least two distinct DIFF values")
        curves.append(SweepCurve(width, values[:, 0], values[:, 1]))

    # CSV의 열 순서와 관계없이 폭이 작은 순서로 비교한다.
    curves.sort(key=lambda curve: curve.width_m)
    if len({curve.width_m for curve in curves}) != len(curves):
        raise ValueError(f"{path.name}: duplicate sweep widths")
    return curves


# 2. 측정값 요약: sweep 안의 지연 최솟값/최댓값과 해당 DIFF를 계산한다.
def summarize(curves, device, metric, delay_unit):
    rows = []
    for curve in curves:
        low = int(np.argmin(curve.delay))
        peak = int(np.argmax(curve.delay))
        rows.append(
            {
                "device": device,
                "metric": f"f_delay_{metric}",
                "parameter": DEVICES[device],
                "width_um": curve.width_m * 1e6,
                "points": len(curve.x_v),
                "delay_unit": delay_unit,
                "min_delay": curve.delay[low],
                "diff_at_min_mV": curve.x_v[low] * 1e3,
                "peak_delay": curve.delay[peak],
                "diff_at_peak_mV": curve.x_v[peak] * 1e3,
            }
        )
    return rows


# 3. 그래프 출력: 동일한 사이즈는 avg/max 그래프에서 같은 색을 사용한다.
def plot_device(device, sweeps, delay_unit):
    widths = sorted({curve.width_m for curves in sweeps.values() for curve in curves})
    colors = dict(zip(widths, plt.get_cmap("viridis")(np.linspace(0.15, 0.85, len(widths)))))
    fig, axes = plt.subplots(
        1, len(sweeps), figsize=(6 * len(sweeps), 4.5),
        squeeze=False, sharex=True, sharey=True, constrained_layout=True,
    )
    for ax, (metric, curves) in zip(axes[0], sweeps.items()):
        for curve in curves:
            ax.plot(
                curve.x_v * 1e3, curve.delay, "o-",
                color=colors[curve.width_m], markersize=3, linewidth=1.3,
                label=f"W = {curve.width_m * 1e6:.6g} um",
            )
        ax.set_title(METRICS[metric])
        ax.set_xlabel("DIFF (mV)")
        ax.set_ylabel(f"Delay ({delay_unit})")
        ax.grid(True, alpha=0.3)
        ax.legend(title=DEVICES[device])
    fig.suptitle(f"{device}: transistor width sweep")
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--device", nargs="+", choices=list(DEVICES), default=list(DEVICES))
    parser.add_argument("--metric", nargs="+", choices=list(METRICS), default=list(METRICS))
    parser.add_argument("--input-dir", type=Path, default=BASE_DIR)
    parser.add_argument("--output-dir", type=Path, default=BASE_DIR / "results" / "f_delay")
    parser.add_argument("--delay-unit", default="CSV units", help="Label only; CSV delay values are not rescaled")
    parser.add_argument("--no-show", action="store_true", help="Save figures without opening plot windows")
    args = parser.parse_args()
    devices = list(dict.fromkeys(args.device))
    metrics = list(dict.fromkeys(args.metric))

    # 모든 입력을 먼저 읽어, 파일명이나 헤더 오류가 있으면 저장 전에 알린다.
    sweeps = {}
    try:
        for device in devices:
            sweeps[device] = {
                metric: load_sweep(
                    args.input_dir / f"f_delay_{metric}_{device}_sweep.csv", device, metric
                )
                for metric in metrics
            }
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Input error: {exc}\n")

    # 4. 결과 출력 및 저장
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    figures = []
    for device, device_sweeps in sweeps.items():
        for metric, curves in device_sweeps.items():
            rows.extend(summarize(curves, device, metric, args.delay_unit))
        fig = plot_device(device, device_sweeps, args.delay_unit)
        filename = f"f_delay_{'_'.join(metrics)}_{device}_sweep.png"
        fig.savefig(args.output_dir / filename, dpi=200)
        figures.append(fig)

    summary = pd.DataFrame(rows)
    summary_path = args.output_dir / "f_delay_summary.csv"
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    print(f"Delay values use {args.delay_unit}; values have not been rescaled.")
    print("Peaks are observed sample maxima over DIFF, not fitted maxima.")
    print(summary.to_string(index=False, float_format=lambda value: f"{value:.6g}"))
    print(f"\nFigures and summary saved to: {args.output_dir.resolve()}")
    print(f"Summary: {summary_path.name} (replaced on each run)")

    # 5. 그래프 표시
    if not args.no_show:
        plt.show()
    for fig in figures:
        plt.close(fig)


if __name__ == "__main__":
    main()
