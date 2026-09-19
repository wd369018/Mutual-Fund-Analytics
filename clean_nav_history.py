"""
Clean NAV history data from raw AMFI CSV.

Reads: data/raw/02_nav_history.csv
Writes: data/processed/Cleaned_02_nav_history.csv

Processes:
- Parses date column to datetime
- Sorts by amfi_code + date
- Removes duplicates (keeps last)
- Validates NAV > 0
- Forward-fills missing NAV for holidays/weekends
- Removes remaining NAV <= 0 after ffill
- Resets index
- Saves cleaned CSV
"""
import pandas as pd
from pathlib import Path

BASE = Path('C:/Users/wd369/OneDrive/Desktop/myrepo/Mutual-Fund-Analytics')
RAW = BASE / 'data' / 'raw'
PROCESSED = BASE / 'data' / 'processed'


def clean_nav_history():
    """Load, clean, and save NAV history data."""
    # Load raw NAV data
    nav = pd.read_csv(RAW / '02_nav_history.csv')

    # Parse dates to datetime
    nav['date'] = pd.to_datetime(nav['date'], format='%Y-%m-%d')

    # Sort by amfi_code + date
    nav = nav.sort_values(['amfi_code', 'date'])

    # Remove duplicates (keep last as per original logic)
    nav = nav.drop_duplicates(subset=['amfi_code', 'date'], keep='last')

    # Validate NAV > 0
    nav = nav[nav['nav'] > 0].copy()

    # Forward-fill missing NAV for holidays/weekends
    # Group by amfi_code and forward-fill NAV
    nav['nav'] = nav.groupby('amfi_code')['nav'].ffill()

    # Remove any remaining NAV <= 0 after ffill
    nav = nav[nav['nav'] > 0].copy()

    # Reset index
    nav = nav.reset_index(drop=True)

    # Save cleaned data
    output_path = PROCESSED / 'Cleaned_02_nav_history.csv'
    nav.to_csv(output_path, index=False)

    return nav


if __name__ == '__main__':
    nav = clean_nav_history()
    print(f'Cleaned NAV shape: {nav.shape}')
    print(f'Saved to: {PROCESSED / "Cleaned_02_nav_history.csv"}')
    print(f'Date range: {nav["date"].min()} to {nav["date"].max()}')
    print(f'Unique funds: {nav["amfi_code"].nunique()}')
    print(f'Total records: {len(nav)}')