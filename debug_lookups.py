import pandas as pd
from pathlib import Path
import sqlite3

BASE = Path('C:/Users/wd369/OneDrive/Desktop/myrepo/Mutual-Fund-Analytics')
PROCESSED = BASE / 'data' / 'processed'

# Load cleaned data
txn = pd.read_csv(PROCESSED / 'Cleaned_08_investor_transactions.csv')
nav = pd.read_csv(PROCESSED / 'Cleaned_02_nav_history.csv')

print("Transaction amfi_code sample:", txn['amfi_code'].unique()[:5])
print("Transaction amfi_code dtype:", txn['amfi_code'].dtype)
print()

# Load fund master
fund = pd.read_csv(PROCESSED / 'Cleaned_01_data_fund_master.csv')
print("Fund master amfi_code sample:", fund['amfi_code'].unique()[:5])
print("Fund master amfi_code dtype:", fund['amfi_code'].dtype)
print()

# Check if any transaction amfi_codes exist in fund master
txn_codes = set(txn['amfi_code'].astype(int).unique())
fund_codes = set(fund['amfi_code'].astype(int).unique())
print(f"Transaction codes in fund master: {len(txn_codes & fund_codes)}/{len(txn_codes)}")
print(f"Missing from fund master: {len(txn_codes - fund_codes)}")
print(f"Extra in fund master: {len(fund_codes - txn_codes)}")

# Check date formats
print(f"\nTransaction date sample: {txn['transaction_date'].unique()[:3]}")
print(f"NAV date sample: {nav['date'].unique()[:3]}")