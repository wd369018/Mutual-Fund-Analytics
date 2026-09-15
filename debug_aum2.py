import pandas as pd
from pathlib import Path
import sqlite3

BASE = Path('C:/Users/wd369/OneDrive/Desktop/myrepo/Mutual-Fund-Analytics')
PROCESSED = BASE / 'data' / 'processed'

# Load data
aum = pd.read_csv(RAW / '03_aum_by_fund_house.csv') if False else pd.read_csv(BASE / 'data' / 'raw' / '03_aum_by_fund_house.csv')
fund = pd.read_csv(PROCESSED / 'Cleaned_01_data_fund_master.csv')

print("AUM fund_house unique values:")
for v in aum['fund_house'].unique():
    print(f'  AUM: "{v}"')

print("\nFund master fund_house unique values:")
for v in fund['fund_house'].unique():
    print(f'  FM:  "{v}"')

# Check exact matches
print("\nExact matches:")
for ah in aum['fund_house'].unique():
    fm_matches = fund[fund['fund_house'] == ah]
    print(f'  AUM: "{ah}" == FM: "{ah}" -> {len(fm_matches)} exact matches')

# Check with strip
print("\nStrip matches:")
for ah in aum['fund_house'].unique():
    fm_matches = fund[fund['fund_house'].str.strip() == ah.strip()]
    print(f'  AUM: "{ah.strip()}" -> {len(fm_matches)} strip matches')