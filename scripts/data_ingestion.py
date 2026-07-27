import pandas as pd
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "data", "raw")


csv_files = [
    file for file in os.listdir(DATA_PATH)
    if file.endswith(".csv")
]


print("Total CSV Files Found:", len(csv_files))


print("Total CSV Files Found:", len(csv_files))



for file in csv_files:
    print("\n==============================")
    print("FILE NAME:", file)
    print("==============================")

    file_path = os.path.join(DATA_PATH, file)

    df = pd.read_csv(file_path)

    
    print("\nShape:")
    print(df.shape)

    
    print("\nData Types:")
    print(df.dtypes)

    
    print("\nFirst 5 Rows:")
    print(df.head())

    
    print("\nMissing Values:")
    print(df.isnull().sum())