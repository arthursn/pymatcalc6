"""
This module provides the MatCalcAPI class to interface with the MatCalc DLL.

The MatCalcAPI class allows users to perform calculations, set element compositions,
and retrieve variable values from the MatCalc environment.
"""

import os
import sys
import ctypes
from pathlib import Path
from typing import Optional, Callable, Any, Sequence, Union


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


class MatCalcAPI:
    """A class to interface with the MatCalc DLL for performing calculations.

    This class provides methods to initialize the MatCalc environment,
    execute commands, set element compositions, and retrieve variable values.
    """

    STRLEN_MAX = 1024

    def find_mc_core_library_file(self) -> Path:
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
        self.lib_matcalc = ctypes.CDLL(
            mc_core_library_file or self.find_mc_core_library_file()
        )

        # Load functions using the generic loader
        self.MCC_InitializeExternalConstChar = self.load_dll_function(
            "MCC_InitializeExternalConstChar",
            [ctypes.c_char_p, ctypes.c_bool],
            ctypes.c_bool,
        )

        self.MCCOL_ProcessCommandLineInput = self.load_dll_function(
            "MCCOL_ProcessCommandLineInput", [ctypes.c_char_p], ctypes.c_int
        )

        self.MCCOL_ProcessCommandLineInputNewColine = self.load_dll_function(
            "MCCOL_ProcessCommandLineInputNewColine", [ctypes.c_char_p], ctypes.c_int
        )

        self.MCC_CalcEquilibrium = self.load_dll_function(
            "MCC_CalcEquilibrium", [ctypes.c_bool, ctypes.c_int], ctypes.c_int
        )

        self.MCC_SetTemperature = self.load_dll_function(
            "MCC_SetTemperature", [ctypes.c_double, ctypes.c_bool], ctypes.c_double
        )

        self.MCC_GetMCVariable = self.load_dll_function(
            "MCC_GetMCVariable", [ctypes.c_char_p], ctypes.c_double
        )

    def load_dll_function(
        self,
        func_name: str,
        argtypes: Sequence[ctypes.CFUNCTYPE],
        restype: Any,
    ) -> Callable:
        """Dynamically load a function from the DLL."""
        func = getattr(self.lib_matcalc, func_name)
        func.argtypes = argtypes
        func.restype = restype
        return func

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
