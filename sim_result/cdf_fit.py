
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import norm

# 1. CSV 파일 불러오기
# data = pd.read_csv("cdf_data.csv")
data = pd.read_csv("f_prob_post_layout_60_2.csv")

x = data.iloc[:, 0].to_numpy()  # DIFF [V]
y = data.iloc[:, 1].to_numpy()  # Probability

# 2. Gaussian CDF 모델
def gaussian_cdf(x, mu, sigma):
    return norm.cdf(x, loc=mu, scale=sigma)

# 3. CDF Fitting
popt, pcov = curve_fit(
    gaussian_cdf,
    x,
    y,
    p0=[0, 100e-6],
    bounds=([-np.inf, 1e-12], [np.inf, np.inf])
)

mu, sigma = popt

# 4. 결과 출력
print(f"Mean (mu): {mu*1e6:.3f} uV")
print(f"Input-Referred Noise (sigma): {sigma*1e6:.3f} uV RMS")
print(f"Input-Referred Noise Variance: {(sigma*1e3)**2:.6f} mV^2")

# 5. 그래프 출력
x_fit = np.linspace(min(x), max(x), 500)
y_fit = gaussian_cdf(x_fit, mu, sigma)

plt.figure()
plt.scatter(x*1e3, y, label="Simulation")
plt.plot(x_fit*1e3, y_fit, label="Gaussian CDF Fit")

plt.xlabel("DIFF (mV)")
plt.ylabel("Probability")
plt.legend()
plt.grid(True)
plt.show()
