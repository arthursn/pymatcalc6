# pymatcalc

A Python interface for MatCalc based on the MatCalc C-API.

## Features
- Interface with the MatCalc DLL for performing calculations.
- Methods to initialize the MatCalc environment and execute commands.
- Set element compositions and retrieve variable values.

## Installation
To install pymatcalc, use pip:
```bash
pip install pymatcalc
```

## Usage
You can find an example of how to use pymatcalc in the [`examples`](?path=/examples) folder.

```python
from pymatcalc.api import MatCalcAPI

# application_directory is optional. If unset, the MATCALC_DIR env variable 
# will be used, falling back to the current directory 
api = MatCalcAPI(application_directory="/path/to/matcalc")
api.init()
api.set_temperature_kelvin(300)
result = api.get_variable("some_variable")
print(result)
```

## Troubleshooting

You might encounter the following error in Linux or macOS:

```
OSError: libQt5Network.so.5: cannot open shared object file: No such file or directory
```

You can fix it by adding MatCalc's `/lib` folder (where the shared libraries needed by `mc_core` are) to the `LD_LIBRARY_PATH` env variable:

```
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/path/to/matcalc/lib"
```