# %% [markdown]

# # Calculating Fe-C phase diagram

# Make sure to install the dependencies to run this example with:

# ```bash
# # From the pymatcalc6 root folder
# pip install '.[examples]'
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

ZERO_FRACTION_THRESHOLD = 1e-9

# %%

phases = ["FCC_A1", "BCC_A2", "CEMENTITE"]

# Use supressing_stdout to suppress the stdout output from mc_core
with suppressing_stdout():
    mc = MatCalcAPI()
    mc.execute_command("use-module core")
    mc.execute_command("open-thermodyn-database mc_fe.tdb")
    mc.execute_command("select-element C")
    mc.execute_command(f"select-phase {' '.join(phases)}")
    mc.execute_command("read-thermodyn-database")

# %%

temperature, carbon = np.meshgrid(
    np.linspace(700, 1200, 50),
    np.logspace(-5, -1, 51),
)

phase_map_mask = []

for temp, carb in tqdm.tqdm(
    zip(
        temperature.ravel(),
        carbon.ravel(),
    ),
    total=len(carbon.ravel()),
):
    mask = 0

    with suppressing_stdout():
        try:
            mc.set_temperature_kelvin(temp)
            mc.set_element_mole_fraction("C", carb)
            mc.calculate_equilibrium()
        except Exception:
            pass
        else:
            for p, phase in enumerate(phases):
                if mc.get_variable(f"F${phase}") > ZERO_FRACTION_THRESHOLD:
                    mask |= 1 << p

    phase_map_mask.append(mask)

# %%

plt.pcolormesh(
    carbon,
    temperature,
    np.array(phase_map_mask).reshape(temperature.shape),
)
plt.xscale("log")
plt.xlabel("Carbon concentration (at. fraction)")
plt.ylabel("Temperature (K)")
plt.show()
