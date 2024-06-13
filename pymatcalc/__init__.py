import os

if not os.getenv("MATCALC_DIR"):
    os.environ["MATCALC_DIR"] = "C:/MatCalc"

from .pymatcalc import *
