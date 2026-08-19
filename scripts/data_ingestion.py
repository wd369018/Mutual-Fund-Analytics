"""
Data ingestion module for the Mutual Fund Analytics project.

This script loads and validates raw mutual-fund datasets.
"""


import pandas as pd
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "data", "raw")


csv_files = [
    file for file in os.listdir(DATA_PATH)
    if file.endswith(".csv")
]






for file in csv_files:
    file_path = os.path.join(DATA_PATH, file)

    df = pd.read_csv(file_path)


def main():
    """Run the data ingestion pipeline."""
    # Yahan apna existing ingestion code/function call karo.
    pass


if __name__ == "__main__":
    main()