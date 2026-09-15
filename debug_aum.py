import pandas as pd
from pathlib import Path

BASE = Path('C:/Users/wd369/OneDrive/Desktop/myrepo/Mutual-Fund-Analytics')
RAW = BASE / 'data' / 'raw'
PROCESSED = BASE / 'data' / 'processed'

# Load raw AUM data
aum = pd.read_csv(RAW / '03_aum_by_fund_house.csv')
print("Raw AUM fund_house values (first 20):")
for val in aum['fund_house'].unique()[:20]:
    print(f'  "{val}"')

# Load cleaned fund master
fund = pd.read_csv(PROCESSED / 'Cleaned_01_data_fund_master.csv')
print("\nCleaned fund master fund_house values (first 20):")
for val in fund['fund_house'].unique()[:20]:
    print(f'  "{val}"')

# Check for matches
print("\nMatching fund houses:")
for ah in aum['fund_house'].unique():
    matches = fund[fund['fund_house'].str.contains(ah, case=False, na=False)]
    print(f'  AUM: "{ah}" -> {len(matches)} matches in fund master')