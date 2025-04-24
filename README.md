# pymatcalc6

A pure Python interface for MatCalc 6 based on the MatCalc C-API.

This package does not provide any proprietary MatCalc code or binary. Instead, it wraps MatCalc's mc_core library with [`ctypes`](https://docs.python.org/3/library/ctypes.html), providing a simple Python interface.

## Features

- Interface with the MatCalc DLL for performing calculations.
- Methods to initialize the MatCalc environment and execute commands.

## Dependencies

You must have [MatCalc 6](https://www.matcalc.at/) installed.

Optionally, set the `MATCALC_DIR` environment variable to the path to MatCalc's installation directory (e.g., `C:\Program Files\MatCalc 6.04`).

## Installation

pymatcalc6 is in dev and not yet published to the Python Package Index. To install it, clone this repo and then install pymatcalc6 using pip:

```bash
git clone https://github.com/arthursn/pymatcalc6/
pip install ./pymatcalc6
```

## Usage

You can find an example of how to use pymatcalc6 in the [`examples`](?path=/examples) folder.

To init the API, run:

```python
from pymatcalc6.api import MatCalcAPI

mc = MatCalcAPI(application_directory="/path/to/matcalc/directory")
```

Or, if `MATCALC_DIR` is set, you can simply run:

```python
mc = MatCalcAPI()
```

Then you can run your commands, e.g.:

```python
mc.execute_command("use-module core")
mc.execute_command("open-thermodyn-database mc_fe.tdb")
mc.execute_command("select-element C")
mc.execute_command("select-phase FCC_A1 BCC_A2 CEMENTITE")
mc.execute_command("read-thermodyn-database")
mc.set_temperature_kelvin(800)
mc.set_element_mole_fraction("C", 1e-2)
mc.calculate_equilibrium()
print("Fraction austenite", mc.get_variable("F$FCC_A1"))
print("Fraction ferrite", mc.get_variable("F$BCC_A2"))
print("Fraction cementite", mc.get_variable("F$CEMENTITE"))
```

## Troubleshooting

You might encounter the following error in Linux or macOS:

```
OSError: libQt5Network.so.5: cannot open shared object file: No such file or directory
```

Installing `libqt5network5` might not work because `mc_core` relies on some specific library versions. The easiest way to fix this is setting `LD_LIBRARY_PATH` with MatCalc's `$MATCALC_DIR/lib` folder (where the shared libraries needed by `mc_core` are):

```
LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/path/to/matcalc/lib" python
```

or 

```
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/path/to/matcalc/lib"
```

You are advised to NOT add override your systems `LD_LIBRARY_PATH` (by, for example, adding the command above in your `.bashrc` file) because some of the libraries in `$MATCALC_DIR/lib`, such as `libselinux.so.1`, might clash with the system libraries.