# %% [markdown]

# # Calculating chemical potentials

# Make sure to install the dependencies to run this example with:

# ```bash
# pip install 'git+https://github.com/arthursn/pymatcalc6/[examples]'
# ```

# %%

import tqdm
import numpy as np

from pymatcalc6 import MatCalcAPI
from pymatcalc6.utils import suppressing_stdout, fix_matplotlib_backend

# Fall back to `alternative_backend` if QtAgg is being used by default
# QtAgg cannot be used because of clashing DLLs with MatCalc
fix_matplotlib_backend(alternative_backend="WebAgg")

import matplotlib.pyplot as plt  # noqa: E402

# %%

# Use supressing_stdout to suppress the stdout output from mc_core
with suppressing_stdout():
    mc = MatCalcAPI()
    mc.execute_command("use-module core")
    mc.execute_command("open-thermodyn-database mc_fe.tdb")
    mc.execute_command("select-element C Mn")
    mc.execute_command("select-phase FCC_A1")
    mc.execute_command("read-thermodyn-database")

# %%

temperature, carbon = np.meshgrid(
    np.linspace(700, 1200, 50),
    np.logspace(-5, -1, 51),
)

chemical_potential = {
    "FCC_A1": {
        "C": [],
        "Mn": [],
        "Fe": [],
    },
}

with suppressing_stdout():
    mc.set_element_mole_fraction("Mn", 1e-2)

for temp, carb in tqdm.tqdm(
    zip(
        temperature.ravel(),
        carbon.ravel(),
    ),
    total=len(carbon.ravel()),
):
    with suppressing_stdout():
        mc.set_temperature_kelvin(temp)
        mc.set_element_mole_fraction("C", carb)
        mc.calculate_equilibrium()
        chemical_potential["FCC_A1"]["C"].append(mc.get_variable("MU$C"))
        chemical_potential["FCC_A1"]["Mn"].append(mc.get_variable("MU$Mn"))
        chemical_potential["FCC_A1"]["Fe"].append(mc.get_variable("MU$Fe"))

# %%

fig, axes = plt.subplots(
    1,
    3,
    figsize=(12, 4),
    sharex=True,
    sharey=True,
)
# iter_axes = iter(axes)

for ax, (element, mu) in zip(axes, chemical_potential["FCC_A1"].items()):
    cmap = ax.contour(
        carbon,
        temperature,
        np.array(mu).reshape(temperature.shape),
        levels=20,
    )
    fig.colorbar(cmap, ax=ax)
    ax.set_title(f"Chemical potential of {element} in austenite")

axes[1].set_xscale("log")
axes[1].set_xlabel("Carbon concentration (at. fraction)")
axes[0].set_ylabel("Temperature (K)")

plt.show()
