import pandas as pd
from pathlib import Path

BASE = Path('C:/Users/wd369/OneDrive/Desktop/myrepo/Mutual-Fund-Analytics')
RAW = BASE / 'data' / 'raw'
PROCESSED = BASE / 'data' / 'processed'

# Load raw transactions data
transactions = pd.read_csv(RAW / '08_investor_transactions.csv')

print(f'Raw transactions shape: {transactions.shape}')

# 1. Standardise transaction_type values (SIP/Lumpsum/Redemption)
# The raw data already has correct values, but normalize to title case
transactions['transaction_type'] = transactions['transaction_type'].astype(str).str.strip()

# Define valid transaction types
valid_types = {'SIP', 'Lumpsum', 'Redemption'}

# Map to valid types - if not valid, try matching case-insensitive
def normalize_type(val):
    val = val.strip()
    if val.upper() in [t.upper() for t in valid_types]:
        # Find the properly cased version
        for t in valid_types:
            if t.upper() == val.upper():
                return t
    return val

transactions['transaction_type'] = transactions['transaction_type'].apply(normalize_type)

# 2. Validate amount > 0
transactions = transactions[transactions['amount_inr'] > 0].copy()

# 3. Fix date formats - parse to datetime
transactions['transaction_date'] = pd.to_datetime(transactions['transaction_date'], errors='coerce')

# 4. Check KYC status enum values
print('Unique KYC status values:')
kyc_vals = transactions['kyc_status'].unique()
for val in kyc_vals:
    print(f'  - "{val}"')

# Define expected KYC enum values
expected_kyc = ['Verified', 'Pending', 'Not Verified']

# Standardize KYC status - strip and title case
transactions['kyc_status'] = transactions['kyc_status'].astype(str).str.strip().str.title()

# 5. Reset index
transactions = transactions.reset_index(drop=True)

# Save cleaned data
output_path = PROCESSED / 'Cleaned_08_investor_transactions.csv'
transactions.to_csv(output_path, index=False)

print(f'\nCleaned transactions shape: {transactions.shape}')
print(f'Saved to: {output_path}')
print(f'Transaction type distribution: {transactions["transaction_type"].value_counts().to_dict()}')
print(f'Date range: {transactions["transaction_date"].min()} to {transactions["transaction_date"].max()}')
print(f'KYC status distribution: {transactions["kyc_status"].value_counts().to_dict()}')