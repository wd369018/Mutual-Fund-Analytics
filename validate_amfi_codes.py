import pandas as pd
from pathlib import Path

BASE = Path('C:/Users/wd369/OneDrive/Desktop/myrepo/Mutual-Fund-Analytics')

# Load datasets
fund_master = pd.read_csv(BASE / 'data' / 'raw' / '01_fund_master.csv')
nav_history = pd.read_csv(BASE / 'data' / 'raw' / '02_nav_history.csv')

print('=== AMFI Code Validation ===')
print()

fund_codes = set(fund_master['amfi_code'].astype(int).unique())
nav_codes = set(nav_history['amfi_code'].astype(int).unique())

print(f'Fund Master unique AMFI codes: {len(fund_codes)}')
print(f'NAV History unique AMFI codes: {len(nav_codes)}')
print()

# Check which fund codes are in NAV
in_fund_not_nav = fund_codes - nav_codes
in_nav_not_fund = nav_codes - fund_codes

print(f'AMFI codes in Fund Master but NOT in NAV: {len(in_fund_not_nav)}')
if in_fund_not_nav:
    print(f'  Codes: {sorted(in_fund_not_nav)}')
print()

print(f'AMFI codes in NAV but NOT in Fund Master: {len(in_nav_not_fund)}')
if in_nav_not_fund:
    print(f'  Codes: {sorted(in_nav_not_fund)}')
print()

# Validation
all_in_nav = fund_codes.issubset(nav_codes)
print(f'All fund codes exist in NAV history: {all_in_nav}')

if all_in_nav:
    print('\n✓ Data Quality: PASS - Every AMFI code in fund_master exists in nav_history')
else:
    missing_count = len(in_fund_not_nav)
    print(f'\n✗ Data Quality: {missing_count} fund codes missing from nav_history')
    print('  Recommendation: Investigate missing codes or add NAV data for those funds')

# Summary
total_funds = len(fund_master)
funds_with_nav = len(fund_master[fund_master['amfi_code'].isin(nav_codes)])
print(f'\nFunds with NAV data: {funds_with_nav}/{total_funds}')