import os
import ctypes
from pathlib import Path
from typing import Optional, Callable, Any, Sequence

__all__ = ["MatCalcAPI"]


class MatCalcAPI:
    STRLEN_MAX = 1024

    def __init__(
        self,
        application_directory: Optional[str] = None,
    ) -> None:
        self.application_directory: str = application_directory or os.getenv(
            "MATCALC_DIR", "."
        )

        os.chdir(self.application_directory)

        # Load the DLL
        self.lib_matcalc = ctypes.CDLL(
            str(Path(self.application_directory) / "mc_core.dll")
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
            self.application_directory.encode("utf-8"), True
        )
        self.MCCOL_ProcessCommandLineInput(b"set-working-directory ./")
        self.MCCOL_ProcessCommandLineInput(
            f"set-application-directory {self.application_directory}".encode("utf-8")
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
