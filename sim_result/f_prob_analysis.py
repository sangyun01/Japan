"""Fit all f_prob size sweeps with the Gaussian CDF model in cdf_fit.py.

Examples (after conda activate aiot):
    python f_prob_analysis.py
    python f_prob_analysis.py --device win platch
    python f_prob_analysis.py --no-show

Input: f_prob_{device}_sweep.csv next to this script, with paired X/Y columns.
Output: per-device PNG plots and f_prob_summary.csv in results/f_prob.
X is DIFF in V; Y is probability in [0, 1]; transistor widths are in m.
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import norm


BASE_DIR = Path(__file__).resolve().parent
DEVICES = {
    "win": "W_in_M79",
    "nlatch": "W_nlatch_M68",
    "reset": "W_resetXY_M14",
    "platch": "W_platch_M23",
    "tail": "W_tail_M10",
}
HEADER = re.compile(
    r"f_prob_\s*\((?P<parameter>W_[^=()]+)=(?P<width>[^()]+)\)\s+(?P<axis>[XY])"
)


@dataclass
class ProbabilityCurve:
    width_m: float
    x_v: np.ndarray
    probability: np.ndarray


@dataclass
class FitResult:
    curve: ProbabilityCurve
    mu_v: float
    sigma_v: float
    rmse: float


# 1. CSV 파일 불러오기: 모든 트랜지스터 사이즈의 X/Y 열 쌍을 읽는다.
def load_sweep(path, device):
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
            or any(x_info[key] != y_info[key] for key in ("parameter", "width"))
            or x_info["parameter"] != DEVICES[device]
        ):
            raise ValueError(f"{path.name}: mismatched X/Y headers at column {column + 1}")

        width = float(x_info["width"])
        values = data.iloc[:, column : column + 2].to_numpy(dtype=float)
        if not np.isfinite(width) or width <= 0 or not np.isfinite(values).all():
            raise ValueError(f"{path.name}: nonfinite data or invalid width")
        values = values[np.argsort(values[:, 0])]
        x, probability = values[:, 0], values[:, 1]
        if len(x) < 3 or np.any(np.diff(x) <= 0):
            raise ValueError(f"{path.name}: expected at least three distinct DIFF values")
        if np.any((probability < 0) | (probability > 1)):
            raise ValueError(f"{path.name}: probabilities must be between 0 and 1")
        if not (probability.min() < 0.5 < probability.max()):
            raise ValueError(f"{path.name}: probability sweep must span the 0.5 transition")
        if np.count_nonzero((probability > 0) & (probability < 1)) < 2:
            raise ValueError(f"{path.name}: insufficient transition samples to estimate sigma")
        curves.append(ProbabilityCurve(width, x, probability))

    # platch처럼 열이 내림차순이어도 폭이 작은 순서로 정리한다.
    curves.sort(key=lambda curve: curve.width_m)
    if len({curve.width_m for curve in curves}) != len(curves):
        raise ValueError(f"{path.name}: duplicate sweep widths")
    return curves


# 2. Gaussian CDF 모델: cdf_fit.py와 같은 정의
def gaussian_cdf(x, mu, sigma):
    return norm.cdf(x, loc=mu, scale=sigma)


# 3. CDF 피팅: 초기값과 sigma 양수 제약도 기존 코드와 동일하게 적용한다.
def fit_curve(curve):
    parameters, _ = curve_fit(
        gaussian_cdf,
        curve.x_v,
        curve.probability,
        p0=[0, 100e-6],
        bounds=([-np.inf, 1e-12], [np.inf, np.inf]),
        maxfev=10000,
    )
    mu, sigma = parameters
    if not np.isfinite(parameters).all() or sigma <= 0:
        raise ValueError("CDF fit returned invalid mu or sigma")
    residual = curve.probability - gaussian_cdf(curve.x_v, mu, sigma)
    return FitResult(curve, float(mu), float(sigma), float(np.sqrt(np.mean(residual**2))))


def summary_row(device, fit):
    return {
        "device": device,
        "source_file": f"f_prob_{device}_sweep.csv",
        "parameter": DEVICES[device],
        "width_um": fit.curve.width_m * 1e6,
        "points": len(fit.curve.x_v),
        "mu_uV": fit.mu_v * 1e6,
        "sigma_uV_rms": fit.sigma_v * 1e6,
        "noise_variance_mV2": (fit.sigma_v * 1e3) ** 2,
        "rmse_probability": fit.rmse,
    }


# 4. 그래프 출력: 측정값은 점, Gaussian CDF 피팅은 선으로 표시한다.
def plot_device(device, fits):
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    colors = plt.get_cmap("viridis")(np.linspace(0.15, 0.85, len(fits)))
    for fit, color in zip(fits, colors):
        curve = fit.curve
        x_fit = np.linspace(curve.x_v.min(), curve.x_v.max(), 500)
        ax.scatter(curve.x_v * 1e3, curve.probability, color=color, s=18)
        ax.plot(
            x_fit * 1e3, gaussian_cdf(x_fit, fit.mu_v, fit.sigma_v),
            color=color, linewidth=1.5,
            label=f"W = {curve.width_m * 1e6:.6g} um; sigma = {fit.sigma_v * 1e6:.2f} uV",
        )
    fig.suptitle(f"{device}: Gaussian CDF fit")
    ax.set_title("Points: simulation; lines: fit", fontsize=10)
    ax.set_xlabel("DIFF (mV)")
    ax.set_ylabel("Probability")
    ax.set_ylim(-0.03, 1.03)
    ax.grid(True, alpha=0.3)
    ax.legend(title=DEVICES[device], loc="lower right", fontsize=9)
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--device", nargs="+", choices=list(DEVICES), default=list(DEVICES))
    parser.add_argument("--input-dir", type=Path, default=BASE_DIR)
    parser.add_argument("--output-dir", type=Path, default=BASE_DIR / "results" / "f_prob")
    parser.add_argument("--no-show", action="store_true", help="Save figures without opening plot windows")
    args = parser.parse_args()

    # 모든 입력과 피팅을 확인한 뒤 결과를 저장한다.
    fitted = {}
    try:
        for device in dict.fromkeys(args.device):
            curves = load_sweep(args.input_dir / f"f_prob_{device}_sweep.csv", device)
            fitted[device] = []
            for curve in curves:
                try:
                    fitted[device].append(fit_curve(curve))
                except (ValueError, RuntimeError) as exc:
                    raise ValueError(f"{device}, W={curve.width_m * 1e6:.6g} um: {exc}") from exc
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Analysis error: {exc}\n")

    # 5. 피팅 결과 출력 및 저장
    args.output_dir.mkdir(parents=True, exist_ok=True)
    figures = []
    rows = []
    for device, fits in fitted.items():
        rows.extend(summary_row(device, fit) for fit in fits)
        fig = plot_device(device, fits)
        fig.savefig(args.output_dir / f"f_prob_{device}_cdf_fit.png", dpi=200)
        figures.append(fig)

    summary = pd.DataFrame(rows)
    summary.to_csv(args.output_dir / "f_prob_summary.csv", index=False, encoding="utf-8-sig")
    print("Gaussian CDF least-squares fit, using the same model and initial values as cdf_fit.py.")
    print("mu: input at P=0.5 (uV); sigma: input-referred noise (uV RMS).")
    print("Noise variance: mV^2; RMSE: residual error in probability units.")
    print(summary.to_string(index=False, float_format=lambda value: f"{value:.6g}"))
    print(f"\nResults saved to: {args.output_dir.resolve()}")
    print("f_prob_summary.csv is replaced on each run with the selected devices.")

    if not args.no_show:
        plt.show()
    for fig in figures:
        plt.close(fig)


if __name__ == "__main__":
    main()
