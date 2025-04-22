"""
This module provides the MatCalcAPI class to interface with the MatCalc DLL.

The MatCalcAPI class allows users to perform calculations, set element compositions,
and retrieve variable values from the MatCalc environment.
"""

import os
import sys
import ctypes
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Callable, Union


__all__ = ["MatCalcAPI"]


PathType = Union[Path, str]


def _get_shared_library_extension():
    if sys.platform.startswith("win"):
        return ".dll"
    elif sys.platform.startswith("darwin"):
        return ".dylib"
    elif sys.platform.startswith("linux"):
        return ".so"
    else:
        return "Unknown OS"


class MatCalcAPI(ctypes.CDLL):
    """A class to interface with the MatCalc DLL for performing calculations.

    This class provides methods to initialize the MatCalc environment,
    execute commands, set element compositions, and retrieve variable values.
    """

    @dataclass
    class FunctionSpec:
        name: str
        argtypes: List[type]
        restype: type

    _registered_functions = [
        FunctionSpec(
            name="MCC_InitializeExternalConstChar",
            argtypes=[ctypes.c_char_p, ctypes.c_bool],
            restype=ctypes.c_bool,
        ),
        FunctionSpec(
            name="MCCOL_ProcessCommandLineInput",
            argtypes=[ctypes.c_char_p],
            restype=ctypes.c_int,
        ),
        FunctionSpec(
            name="MCCOL_ProcessCommandLineInputNewColine",
            argtypes=[ctypes.c_char_p],
            restype=ctypes.c_int,
        ),
        FunctionSpec(
            name="MCC_CalcEquilibrium",
            argtypes=[ctypes.c_bool, ctypes.c_int],
            restype=ctypes.c_int,
        ),
        FunctionSpec(
            name="MCC_SetTemperature",
            argtypes=[ctypes.c_double, ctypes.c_bool],
            restype=ctypes.c_double,
        ),
        FunctionSpec(
            name="MCC_GetMCVariable",
            argtypes=[ctypes.c_char_p],
            restype=ctypes.c_double,
        ),
    ]

    def __init__(
        self,
        application_directory: Optional[PathType] = None,
        mc_core_library_file: Optional[PathType] = None,
    ) -> None:
        self.application_directory: Path = Path(
            application_directory or os.getenv("MATCALC_DIR", ".")
        )

        os.chdir(self.application_directory)

        # Load the DLL
        super().__init__(mc_core_library_file or self._find_mc_core_library_file())

        # Register functions
        self._init_registered_functions()

    def _find_mc_core_library_file(self) -> Path:
        """Find the mc_core library file (e.g., mc_core.dll)"""
        shlib_suffix = _get_shared_library_extension()

        matching_files = set()
        for prefix in ["", "lib"]:
            for fpath in self.application_directory.glob(
                f"{prefix}mc_core{shlib_suffix}*"
            ):
                matching_files.add(fpath.resolve())

        if len(matching_files) == 0:
            raise ValueError(
                f"Could not find mc_core library file in '{self.application_directory}'"
            )

        # Sort matching files and return larger one
        return sorted(matching_files, key=lambda file: file.stat().st_size).pop()

    def _init_registered_functions(self) -> Callable:
        """Initialize the registered functions"""
        for func_spec in self._registered_functions:
            func = getattr(self, func_spec.name)
            func.argtypes = func_spec.argtypes
            func.restype = func_spec.restype

    def init(self) -> None:
        """Initialize the MatCalc API by setting the working directory and application directory."""
        self.MCC_InitializeExternalConstChar(
            str(self.application_directory).encode("utf-8"),
            True,
        )
        self.MCCOL_ProcessCommandLineInput(b"set-working-directory ./")
        self.MCCOL_ProcessCommandLineInput(
            f"set-application-directory {str(self.application_directory)}".encode(
                "utf-8"
            )
        )

    def execute_command(self, cmd: str) -> None:
        """Execute a command in the MatCalc environment.

        Args:
            cmd (str): The command to execute.
        """
        error_code = self.MCCOL_ProcessCommandLineInput(cmd.encode("utf-8"))
        if error_code != 0:
            raise RuntimeError(f"Err nr {error_code} while executing '{cmd}'")

    def execute_command_new_coline(self, cmd: str) -> None:
        """Execute a new command in the MatCalc environment.

        Args:
            cmd (str): The command to execute.
        """
        error_code = self.MCCOL_ProcessCommandLineInputNewColine(cmd.encode("utf-8"))
        if error_code != 0:
            raise RuntimeError(f"Err nr {error_code} while executing '{cmd}'")

    def calculate_equilibrium(self) -> None:
        """Calculate the equilibrium state in the MatCalc environment."""
        error_code = self.MCC_CalcEquilibrium(False, 0)
        if error_code != 0:
            raise RuntimeError(f"Err nr {error_code} while calculating equilibrium")

    def set_temperature_kelvin(self, temperature_kelvin: float) -> None:
        """Set the temperature in Kelvin for the MatCalc environment.

        Args:
            temperature_kelvin (float): The temperature in Kelvin to set.
        """
        self.MCC_SetTemperature(temperature_kelvin, False)

    def set_element_mole_fraction(self, element_symbol: str, value: float) -> None:
        """Set the mole fraction of an element in the MatCalc environment.

        Args:
            element_symbol (str): The symbol of the element.
            value (float): The mole fraction to set.
        """
        self.execute_command(f"enter-composition X {element_symbol}={value}")

    def set_element_weight_fraction(self, element_symbol: str, value: float) -> None:
        """Set the weight fraction of an element in the MatCalc environment.

        Args:
            element_symbol (str): The symbol of the element.
            value (float): The weight fraction to set.
        """
        self.execute_command(f"enter-composition W {element_symbol}={value}")

    def set_element_site_fraction(self, element_symbol: str, value: float) -> None:
        """Set the site fraction of an element in the MatCalc environment.

        Args:
            element_symbol (str): The symbol of the element.
            value (float): The site fraction to set.
        """
        self.execute_command(f"enter-composition U {element_symbol}={value}")

    def get_variable(self, variable: str) -> float:
        """Get the value of a variable from the MatCalc environment.

        Args:
            variable (str): The name of the variable to retrieve.

        Returns:
            float: The value of the variable.
        """
        return self.MCC_GetMCVariable(variable.encode("utf-8"))
