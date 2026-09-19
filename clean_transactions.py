"""
Clean investor transactions data from raw AMFI CSV.

Reads: data/raw/08_investor_transactions.csv
Writes: data/processed/Cleaned_08_investor_transactions.csv

Processes:
- Standardises transaction_type values (SIP/Lumpsum/Redemption)
- Validates amount > 0
- Parses date formats to datetime
- Standardises KYC status enum values
- Resets index
- Saves cleaned CSV
"""
import pandas as pd
from pathlib import Path

BASE = Path('C:/Users/wd369/OneDrive/Desktop/myrepo/Mutual-Fund-Analytics')
RAW = BASE / 'data' / 'raw'
PROCESSED = BASE / 'data' / 'processed'


def clean_investor_transactions():
    """Load, clean, and save investor transactions data."""
    # Load raw transactions data
    transactions = pd.read_csv(RAW / '08_investor_transactions.csv')

    # Standardise transaction_type values (SIP/Lumpsum/Redemption)
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

    # Validate amount > 0
    transactions = transactions[transactions['amount_inr'] > 0].copy()

    # Fix date formats - parse to datetime
    transactions['transaction_date'] = pd.to_datetime(transactions['transaction_date'], errors='coerce')

    # Standardise KYC status - strip and title case
    transactions['kyc_status'] = transactions['kyc_status'].astype(str).str.strip().str.title()

    # Reset index
    transactions = transactions.reset_index(drop=True)

    # Save cleaned data
    output_path = PROCESSED / 'Cleaned_08_investor_transactions.csv'
    transactions.to_csv(output_path, index=False)

    return transactions


if __name__ == '__main__':
    clean_investor_transactions()