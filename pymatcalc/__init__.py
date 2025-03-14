import os
from .api import MatCalcAPI

if not os.getenv("MATCALC_DIR"):
    os.environ["MATCALC_DIR"] = "C:/MatCalc"

__all__ = ["MatCalcAPI"]
