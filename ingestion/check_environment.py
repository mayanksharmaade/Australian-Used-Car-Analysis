import sys
import pandas as pd
import numpy as np
import pyodbc
import yaml


def main():
    print("=== ENVIRONMENT CHECK ===")
    print(f"Python:  {sys.version.split()[0]}")
    print(f"Pandas:  {pd.__version__}")
    print(f"NumPy:   {np.__version__}")
    print(f"pyodbc:  {pyodbc.version}")
    print(f"PyYAML:  {yaml.__version__}")

    drivers = pyodbc.drivers()

    if "ODBC Driver 18 for SQL Server" not in drivers:
        raise RuntimeError(
            "ODBC Driver 18 for SQL Server was not found."
        )

    print("ODBC Driver 18 for SQL Server: FOUND")
    print("Environment check PASSED.")


if __name__ == "__main__":
    main()
