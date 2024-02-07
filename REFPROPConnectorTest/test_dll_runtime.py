# %% IMPORT MODULES
from REFPROPConnector import ThermodynamicPoint
from matplotlib import pyplot as plt
from pandas import DataFrame
import seaborn as sns
import numpy as np
import random
import time


# %% REFERENCE POINT
tp = ThermodynamicPoint(["Carbon Dioxide"], [1])
tp.set_variable("T", 100)
tp.set_variable("P", 0.1)
p = tp.get_variable("P")
t = tp.get_variable("T")
h = tp.get_variable("h")
s = tp.get_variable("s")
rho = tp.get_variable("rho")

n_points = 1000000


# %% T-P Flash
tp_times = np.empty(n_points)
tp_times[:] = np.nan
for i in range(n_points):

    random_mod = random.random() - 0.5
    mult = (1 + random_mod / 10)

    tp.set_variable("T", 100*mult)
    tp.set_variable("P", 0.1*mult)

    start = time.perf_counter()
    tp.get_variable("h")
    tp.get_variable("s")
    tp.get_variable("rho")
    time_tp = (time.perf_counter() - start) * 1000

    if time_tp < 1:
        tp_times[i] = time_tp

sigma = np.nanstd(tp_times)
mean = np.nanmean(tp_times)
tp_times[np.where(np.abs(tp_times - mean) > 6 * sigma)] = np.nan


# %% P-RHO flash
prho_times = np.empty(n_points)
prho_times[:] = np.nan

for i in range(n_points):
    random_mod = random.random() - 0.5
    mult = (1 + random_mod / 10)
    tp.set_variable("P", p * mult)
    tp.set_variable("rho", rho * mult)

    start = time.perf_counter()
    tp.get_variable("h")
    tp.get_variable("T")
    tp.get_variable("s")
    time_prho = (time.perf_counter() - start) * 1000

    if time_prho < 1.5:

        prho_times[i] = time_prho

sigma = np.nanstd(prho_times)
mean = np.nanmean(prho_times)
prho_times[np.where(np.abs(prho_times - mean) > 6 * sigma)] = np.nan


# %% S-H flash
sh_times = np.empty(n_points)
sh_times[:] = np.nan

for i in range(n_points):

    random_mod = random.random() - 0.5
    mult = (1 + random_mod / 10)
    tp.set_variable("S", s * mult)
    tp.set_variable("H", h * mult)

    start = time.perf_counter()
    tp.get_variable("P")
    tp.get_variable("T")
    tp.get_variable("rho")
    time_sh = (time.perf_counter() - start) * 1000

    if time_sh < 1.5:
        sh_times[i] = time_sh

sigma = np.nanstd(sh_times)
mean = np.nanmean(sh_times)
sh_times[np.where(np.abs(sh_times - mean) > 6 * sigma)] = np.nan


# %% P-H flash
ph_times = np.empty(n_points)
ph_times[:] = np.nan

for i in range(n_points):

    random_mod = random.random() - 0.5
    mult = (1 + random_mod / 10)
    tp.set_variable("P", p * mult)
    tp.set_variable("H", h * mult)

    start = time.perf_counter()
    tp.get_variable("h")
    tp.get_variable("T")
    tp.get_variable("rho")
    time_ph = (time.perf_counter() - start) * 1000

    if time_ph < 1.5:
        ph_times[i] = time_ph

sigma = np.nanstd(ph_times)
mean = np.nanmean(ph_times)
ph_times[np.where(np.abs(ph_times - mean) > 6 * sigma)] = np.nan


# %% PLOT_HISTS
data = {

    "T-p flash": tp_times,
    "p-rho flash": prho_times,
    "p-h flash": ph_times,
    "s-h flash": sh_times

}
df = DataFrame(data)
sns.kdeplot(data=df, palette=['orange', 'blue', 'red', 'green'], fill=True)
plt.yscale("log")
plt.show()
