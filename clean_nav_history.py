import pandas as pd
from pathlib import Path

BASE = Path('C:/Users/wd369/OneDrive/Desktop/myrepo/Mutual-Fund-Analytics')
RAW = BASE / 'data' / 'raw'
PROCESSED = BASE / 'data' / 'processed'

# Load raw NAV data
nav = pd.read_csv(RAW / '02_nav_history.csv')

print(f'Raw NAV shape: {nav.shape}')
print(f'Columns: {list(nav.columns)}')

# 1. Parse dates to datetime
nav['date'] = pd.to_datetime(nav['date'], format='%Y-%m-%d')

# 2. Sort by amfi_code + date
nav = nav.sort_values(['amfi_code', 'date'])

# 3. Remove duplicates (keep last as per original logic)
nav = nav.drop_duplicates(subset=['amfi_code', 'date'], keep='last')

# 4. Validate NAV > 0
nav = nav[nav['nav'] > 0].copy()

# 5. Forward-fill missing NAV for holidays/weekends
# Group by amfi_code and forward-fill NAV
nav['nav'] = nav.groupby('amfi_code')['nav'].ffill()

# Remove any remaining NAV <= 0 after ffill
nav = nav[nav['nav'] > 0].copy()

# Reset index
nav = nav.reset_index(drop=True)

# Save cleaned data
output_path = PROCESSED / 'Cleaned_02_nav_history.csv'
nav.to_csv(output_path, index=False)

print(f'\nCleaned NAV shape: {nav.shape}')
print(f'Saved to: {output_path}')
print(f'Date range: {nav["date"].min()} to {nav["date"].max()}')
print(f'Unique funds: {nav["amfi_code"].nunique()}')
print(f'Total records: {len(nav)}')