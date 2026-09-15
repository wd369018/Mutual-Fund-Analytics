import pandas as pd
from pathlib import Path
import sqlite3

BASE = Path('C:/Users/wd369/OneDrive/Desktop/myrepo/Mutual-Fund-Analytics')
PROCESSED = BASE / 'data' / 'processed'

# Load cleaned data
txn = pd.read_csv(PROCESSED / 'Cleaned_08_investor_transactions.csv')
nav = pd.read_csv(PROCESSED / 'Cleaned_02_nav_history.csv')

# Connect to DB
conn = sqlite3.connect(BASE / 'database' / 'bluestock_mf.db')

# Check dim_date
print("dim_date count:", conn.execute("SELECT COUNT(*) FROM dim_date").fetchone()[0])
print("Sample dim_date rows:")
for row in conn.execute("SELECT date_key, full_date FROM dim_date LIMIT 5"):
    print(f"  {row}")

# Check date lookup
date_lookup = {}
for row in conn.execute("SELECT date_key, full_date FROM dim_date"):
    date_lookup[row[1]] = int(row[0])

print(f"\nDate lookup count: {len(date_lookup)}")

# Check transaction dates in lookup
txn_dates = txn['transaction_date'].unique()[:5]
print(f"\nTransaction dates to check: {txn_dates}")

for d in txn_dates:
    if d in date_lookup:
        print(f"  '{d}' FOUND -> key {date_lookup[d]}")
    else:
        print(f"  '{d}' NOT FOUND")

# Check NAV dates in lookup
nav_dates = nav['date'].unique()[:5]
print(f"\nNAV dates to check: {nav_dates}")

for d in nav_dates:
    if d in date_lookup:
        print(f"  '{d}' FOUND -> key {date_lookup[d]}")
    else:
        print(f"  '{d}' NOT FOUND")

conn.close()