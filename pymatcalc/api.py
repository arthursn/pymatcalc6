import os
import ctypes
from typing import Optional

__all__ = ["MatCalcAPI"]


class MatCalcAPI:
    STRLEN_MAX = 1024

    def __init__(
        self,
        application_directory: Optional[str] = None,
    ) -> None:
        self.application_directory = application_directory

        if self.application_directory is None:
            self.application_directory = os.getenv("MATCALC_DIR", ".")

        os.chdir(self.application_directory)

        # Load the DLL
        self.lib_matcalc = ctypes.CDLL(
            os.path.join(self.application_directory, "mc_core.dll")
        )

        # Load functions
        self.MCC_InitializeExternalConstChar = (
            self.lib_matcalc.MCC_InitializeExternalConstChar
        )
        self.MCC_InitializeExternalConstChar.argtypes = [ctypes.c_char_p, ctypes.c_bool]
        self.MCC_InitializeExternalConstChar.restype = ctypes.c_bool

        self.MCCOL_ProcessCommandLineInput = (
            self.lib_matcalc.MCCOL_ProcessCommandLineInput
        )
        self.MCCOL_ProcessCommandLineInput.argtypes = [ctypes.c_char_p]
        self.MCCOL_ProcessCommandLineInput.restype = ctypes.c_int

        self.MCCOL_ProcessCommandLineInputNewColine = (
            self.lib_matcalc.MCCOL_ProcessCommandLineInputNewColine
        )
        self.MCCOL_ProcessCommandLineInputNewColine.argtypes = [ctypes.c_char_p]
        self.MCCOL_ProcessCommandLineInputNewColine.restype = ctypes.c_int

        self.MCC_CalcEquilibrium = self.lib_matcalc.MCC_CalcEquilibrium
        self.MCC_CalcEquilibrium.argtypes = [ctypes.c_bool, ctypes.c_int]
        self.MCC_CalcEquilibrium.restype = ctypes.c_int

        self.MCC_SetTemperature = self.lib_matcalc.MCC_SetTemperature
        self.MCC_SetTemperature.argtypes = [ctypes.c_double, ctypes.c_bool]
        self.MCC_SetTemperature.restype = ctypes.c_double

        self.MCC_GetMCVariable = self.lib_matcalc.MCC_GetMCVariable
        self.MCC_GetMCVariable.argtypes = [ctypes.c_char_p]
        self.MCC_GetMCVariable.restype = ctypes.c_double

    def init(self):
        self.MCC_InitializeExternalConstChar(
            self.application_directory.encode("utf-8"), True
        )
        self.MCCOL_ProcessCommandLineInput(b"set-working-directory ./")
        self.MCCOL_ProcessCommandLineInput(
            f"set-application-directory {self.application_directory}".encode("utf-8")
        )

    def execute_command(
        self,
        cmd: str,
    ) -> None:
        error_code = self.MCCOL_ProcessCommandLineInput(cmd.encode("utf-8"))
        if error_code != 0:
            raise RuntimeError(f"Err nr {error_code} while executing '{cmd}'")

    def execute_command_new_coline(
        self,
        cmd: str,
    ) -> None:
        error_code = self.MCCOL_ProcessCommandLineInputNewColine(cmd.encode("utf-8"))
        if error_code != 0:
            raise RuntimeError(f"Err nr {error_code} while executing '{cmd}'")

    def calculate_equilibrium(
        self,
    ) -> None:
        error_code = self.MCC_CalcEquilibrium(False, 0)
        if error_code != 0:
            raise RuntimeError(f"Err nr {error_code} while calculating equilibrium")

    def set_temperature_kelvin(
        self,
        temperature_kelvin: float,
    ) -> None:
        self.MCC_SetTemperature(temperature_kelvin, False)

    def set_element_mole_fraction(
        self,
        element_symbol: str,
        value: float,
    ) -> None:
        self.execute_command(f"enter-composition X {element_symbol}={value}")

    def set_element_weight_fraction(
        self,
        element_symbol: str,
        value: float,
    ) -> None:
        self.execute_command(f"enter-composition W {element_symbol}={value}")

    def set_element_site_fraction(
        self,
        element_symbol: str,
        value: float,
    ) -> None:
        self.execute_command(f"enter-composition U {element_symbol}={value}")

    def get_variable(self, variable: str) -> float:
        return self.MCC_GetMCVariable(variable.encode("utf-8"))
