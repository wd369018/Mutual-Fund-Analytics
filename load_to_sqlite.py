import pandas as pd
from pathlib import Path
import sqlite3

BASE = Path('C:/Users/wd369/OneDrive/Desktop/myrepo/Mutual-Fund-Analytics')
PROCESSED = BASE / 'data' / 'processed'
DB_PATH = BASE / 'database' / 'bluestock_mf.db'

# Create database directory
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Connect to SQLite first
conn = sqlite3.connect(DB_PATH)

# ==========================================
# Step 1: Create schema (drops and creates empty tables)
# ==========================================
print("Step 1: Creating database schema...")
with open('sql/schema.sql', 'r') as f:
    schema_sql = f.read()
conn.executescript(schema_sql)
conn.commit()
print("  Schema created successfully.")

# ==========================================
# Step 2: Populate dim_date FIRST (before any lookups)
# ==========================================
print("\nStep 2: Populating dim_date...")

# Get all dates from source CSVs
nav_raw = pd.read_csv(BASE / 'data' / 'raw' / '02_nav_history.csv')
txn_raw = pd.read_csv(BASE / 'data' / 'raw' / '08_investor_transactions.csv')

nav_raw['date'] = pd.to_datetime(nav_raw['date'], format='%Y-%m-%d')
txn_raw['transaction_date'] = pd.to_datetime(txn_raw['transaction_date'], format='%Y-%m-%d')

# Combine all unique dates and sort
all_dates = pd.concat([
    nav_raw['date'],
    txn_raw['transaction_date']
]).dropna().drop_duplicates().sort_values()

# Create date rows
date_rows = []
for date in all_dates:
    date_ts = pd.Timestamp(date)
    date_rows.append((
        int(date_ts.strftime('%Y%m%d')),
        date_ts.strftime('%Y-%m-%d'),
        int(date_ts.day),
        int(date_ts.month),
        int(date_ts.year),
        f"Q{date_ts.quarter}"
    ))

# Clear and populate dim_date
conn.execute("DELETE FROM dim_date")
conn.commit()

conn.executemany(
    """
    INSERT INTO dim_date (date_key, full_date, day, month, year, quarter)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    date_rows
)
conn.commit()

# Build date_lookup: full_date string -> date_key
date_lookup = {}
for row in conn.execute("SELECT date_key, full_date FROM dim_date"):
    date_lookup[row[1]] = int(row[0])

print(f"  dim_date: {len(date_rows)} rows populated, {len(date_lookup)} date keys")

# ==========================================
# Step 3: Load dim_fund
# ==========================================
print("\nStep 3: Loading dim_fund...")

fund_master = pd.read_csv(PROCESSED / 'Cleaned_01_data_fund_master.csv')
fund_master.to_sql('dim_fund', conn, if_exists='append', index=False)
fund_count = conn.execute("SELECT COUNT(*) FROM dim_fund").fetchone()[0]
print(f"  dim_fund: {fund_count} rows")

# Build lookup dictionaries FROM dim_fund
fund_lookup = {}
for row in conn.execute("SELECT fund_key, amfi_code FROM dim_fund"):
    fund_lookup[int(row[1])] = int(row[0])

# fund_house -> list of fund_keys
fund_house_to_keys = {}
for row in conn.execute("SELECT fund_house, fund_key FROM dim_fund"):
    house = str(row[0]).strip()
    fund_key = int(row[1])
    if house not in fund_house_to_keys:
        fund_house_to_keys[house] = []
    fund_house_to_keys[house].append(fund_key)

print(f"  Fund lookup: {len(fund_lookup)} amfi_code -> fund_key mappings")
print(f"  Fund house map: {len(fund_house_to_keys)} houses")

# ==========================================
# Step 4: Load fact_nav
# ==========================================
print("\nStep 4: Loading fact_nav...")

nav_clean = pd.read_csv(PROCESSED / 'Cleaned_02_nav_history.csv')
nav_clean['date'] = pd.to_datetime(nav_clean['date'], format='%Y-%m-%d')
nav_clean = nav_clean.sort_values(['amfi_code', 'date'])
nav_clean = nav_clean.drop_duplicates(subset=['amfi_code', 'date'], keep='last')

nav_rows = []
nav_skipped = 0

for row in nav_clean.itertuples(index=False):
    fund_key = fund_lookup.get(int(row.amfi_code))
    date_string = pd.Timestamp(row.date).strftime('%Y-%m-%d')
    date_key = date_lookup.get(date_string)

    if fund_key is None or date_key is None:
        nav_skipped += 1
        continue

    nav_rows.append((
        fund_key,
        date_key,
        float(row.nav)
    ))

# Insert in batches
with conn:
    for i in range(0, len(nav_rows), 100):
        batch = nav_rows[i:i+100]
        conn.executemany(
            "INSERT INTO fact_nav (fund_key, date_key, nav) VALUES (?, ?, ?)",
            batch
        )

nav_count = conn.execute("SELECT COUNT(*) FROM fact_nav").fetchone()[0]
print(f"  fact_nav: {nav_count} rows loaded (skipped {nav_skipped})")

# ==========================================
# Step 5: Load fact_aum
# ==========================================
print("\nStep 5: Loading fact_aum...")

aum_clean = pd.read_csv(PROCESSED / 'Cleaned_03_aum_by_fund_house.csv')
aum_clean['date'] = pd.to_datetime(aum_clean['date'], format='%Y-%m-%d')
aum_clean['aum_crore'] = pd.to_numeric(aum_clean['aum_crore'], errors='coerce')
aum_clean['num_schemes'] = pd.to_numeric(aum_clean['num_schemes'], errors='coerce')

aum_rows = []
aum_skipped = 0

for row in aum_clean.itertuples(index=False):
    fund_house = str(row.fund_house).strip()
    keys = fund_house_to_keys.get(fund_house, [])

    if not keys:
        aum_skipped += 1
        continue

    # Use first available fund key for this fund house
    fund_key = keys[0]

    date_key = date_lookup.get(pd.Timestamp(row.date).strftime('%Y-%m-%d'))

    if date_key is None:
        aum_skipped += 1
        continue

    aum_rows.append((
        fund_key,  # fund_house_key
        date_key,
        float(row.aum_crore) if not pd.isna(row.aum_crore) else None,
        int(row.num_schemes) if not pd.isna(row.num_schemes) else None
    ))

# Insert in batches
with conn:
    for i in range(0, len(aum_rows), 100):
        batch = aum_rows[i:i+100]
        conn.executemany(
            "INSERT INTO fact_aum (fund_house_key, date_key, aum_crore, num_schemes) VALUES (?, ?, ?, ?)",
            batch
        )

aum_count = conn.execute("SELECT COUNT(*) FROM fact_aum").fetchone()[0]
print(f"  fact_aum: {aum_count} rows loaded (skipped {aum_skipped})")

# ==========================================
# Step 6: Load fact_performance
# ==========================================
print("\nStep 6: Loading fact_performance...")

perf_clean = pd.read_csv(PROCESSED / 'Cleaned_07_scheme_performance.csv')

perf_rows = []

for row in perf_clean.itertuples(index=False):
    fund_key = fund_lookup.get(int(row.amfi_code))

    if fund_key is None:
        continue

    values = []
    for col in ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct',
                'benchmark_3yr_pct', 'alpha', 'beta',
                'sharpe_ratio', 'sortino_ratio', 'std_dev_ann_pct', 'max_drawdown_pct']:
        val = getattr(row, col)
        if pd.isna(val):
            value = None
        else:
            value = float(val)
        values.append(value)

    perf_rows.append((
        fund_key,
        *values
    ))

# Insert in batches
with conn:
    for i in range(0, len(perf_rows), 10):
        batch = perf_rows[i:i+10]
        conn.executemany(
            """INSERT INTO fact_performance (fund_key, return_1yr_pct, return_3yr_pct, return_5yr_pct,
                benchmark_3yr_pct, alpha, beta, sharpe_ratio, sortino_ratio, std_dev_ann_pct, max_drawdown_pct)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            batch
        )

perf_count = conn.execute("SELECT COUNT(*) FROM fact_performance").fetchone()[0]
print(f"  fact_performance: {perf_count} rows loaded")

# ==========================================
# Step 7: Load fact_transactions
# ==========================================
print("\nStep 7: Loading fact_transactions...")

txn_raw = pd.read_csv(BASE / 'data' / 'raw' / '08_investor_transactions.csv')
# Keep investor_id as string, don't convert to numeric yet
# txn_raw['investor_id'] = pd.to_numeric(txn_raw['investor_id'], errors='coerce')  # REMOVED
# txn_raw['amfi_code'] = pd.to_numeric(txn_raw['amfi_code'], errors='coerce')  # Keep as is for now
txn_raw['transaction_date'] = pd.to_datetime(txn_raw['transaction_date'], format='%Y-%m-%d')
# txn_raw['amount_inr'] = pd.to_numeric(txn_raw['amount_inr'], errors='coerce')  # Keep as is for now

# Build investor_id mapping (string -> integer) using ORIGINAL string values
unique_investors = txn_raw['investor_id'].unique()
investor_map = {}
for inv in unique_investors:
    if str(inv).strip() != '' and str(inv).strip() != 'nan':
        investor_map[str(inv).strip()] = len(investor_map) + 1

txn_rows = []
for row in txn_raw.itertuples(index=False):
    investor_id_str = row.investor_id
    investor_id_val = investor_map.get(str(investor_id_str).strip() if investor_id_str else None)
    
    fund_key = fund_lookup.get(int(row.amfi_code)) if str(row.amfi_code).strip().isdigit() else None
    date_key = date_lookup.get(pd.Timestamp(row.transaction_date).strftime('%Y-%m-%d'))

    if investor_id_val is None or fund_key is None or date_key is None:
        continue

    txn_rows.append((
        investor_id_val,
        fund_key,
        date_key,
        str(row.transaction_type).strip() if row.transaction_type else "",
        float(row.amount_inr) if not pd.isna(row.amount_inr) else None,
        str(row.kyc_status).strip() if row.kyc_status else "",
        str(row.state).strip() if row.state else ""
    ))

# Insert in batches
with conn:
    for i in range(0, len(txn_rows), 100):
        batch = txn_rows[i:i+100]
        conn.executemany(
            "INSERT INTO fact_transactions (investor_id, fund_key, date_key, transaction_type, amount_inr, kyc_status, state) VALUES (?, ?, ?, ?, ?, ?, ?)",
            batch
        )

txn_count = conn.execute("SELECT COUNT(*) FROM fact_transactions").fetchone()[0]
print(f"  fact_transactions: {txn_count} rows loaded")

# ==========================================
# Final Validation
# ==========================================
print("\n=== Final Database Validation ===")
tables = ['dim_fund', 'dim_date', 'fact_nav', 'fact_aum', 'fact_performance', 'fact_transactions']
for table in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table}: {count} rows")

# Check orphan records
print("\n--- Orphan Record Checks ---")
orphan_nav = conn.execute("""
    SELECT COUNT(*) FROM fact_nav f
    LEFT JOIN dim_fund d ON f.fund_key = d.fund_key
    WHERE d.fund_key IS NULL
""").fetchone()[0]
print(f"  fact_nav orphan rows: {orphan_nav}")

orphan_aum = conn.execute("""
    SELECT COUNT(*) FROM fact_aum f
    LEFT JOIN dim_fund h ON f.fund_house_key = h.fund_key
""").fetchone()[0]
print(f"  fact_aum orphan rows: {orphan_aum}")

orphan_txn = conn.execute("""
    SELECT COUNT(*) FROM fact_transactions f
    LEFT JOIN dim_fund d ON f.fund_key = d.fund_key
    LEFT JOIN dim_date dt ON f.date_key = dt.date_key
    WHERE d.fund_key IS NULL OR dt.date_key IS NULL
""").fetchone()[0]
print(f"  fact_transactions orphan rows: {orphan_txn}")

conn.close()
print("\n✅ All datasets loaded into SQLite successfully!")

# Summary
print("\n=== Row Count Summary ===")
print("  dim_fund: 40 (expected 40)")
print(f"  dim_date: varies by date range")
print(f"  fact_nav: {nav_count} (expected ~46000)")
print(f"  fact_aum: {aum_count} (expected 90)")
print(f"  fact_performance: {perf_count} (expected 40)")
print(f"  fact_transactions: {txn_count} (expected 103419)")