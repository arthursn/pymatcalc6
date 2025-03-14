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

api = MatCalcAPI(application_directory='path/to/matcalc')
api.init()
api.set_temperature_kelvin(300)
result = api.get_variable('some_variable')
print(result)
```
