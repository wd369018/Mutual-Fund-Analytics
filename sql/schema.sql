-- ======================================
-- Dim_fund Tables
-- ======================================
cursor.execute("DROP TABLE IF EXISTS dim_fund;")

cursor.execute("""
CREATE TABLE dim_fund (

    fund_key INTEGER PRIMARY KEY AUTOINCREMENT,

    amfi_code INTEGER UNIQUE,

    fund_house TEXT,

    scheme_name TEXT,

    category TEXT,

    sub_category TEXT,

    plan TEXT,

    launch_date DATE,

    benchmark TEXT,

    expense_ratio_pct REAL,

    exit_load_pct REAL,

    min_sip_amount REAL,

    min_lumpsum_amount REAL,

    fund_manager TEXT,

    risk_category TEXT,

    sebi_category_code TEXT

);
""")

conn.commit()

print("dim_fund created")

fund.to_sql(
    "dim_fund",
    engine,
    if_exists="append",
    index=False
)

-- ======================================
-- Dim_date Tables
-- ======================================

cursor.execute("DROP TABLE IF EXISTS dim_date;")

cursor.execute("""
CREATE TABLE dim_date (

    date_key INTEGER PRIMARY KEY,

    date TEXT,

    year INTEGER,

    month INTEGER,

    quarter INTEGER,

    day INTEGER

);
""")

conn.commit()

print("dim_date created")


-- ======================================
-- Fact_nav Tables
-- ======================================

cursor.execute("DROP TABLE IF EXISTS fact_nav;")

cursor.execute("""
CREATE TABLE fact_nav (

    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,

    fund_key INTEGER,

    date_key INTEGER,

    nav REAL,

    FOREIGN KEY(fund_key)
    REFERENCES dim_fund(fund_key),

    FOREIGN KEY(date_key)
    REFERENCES dim_date(date_key)

);
""")

conn.commit()

print("fact_nav created")

-- ======================================
-- Fact_transactions Tables
-- ======================================
cursor.execute("DROP TABLE IF EXISTS fact_transactions;")

cursor.execute("""
CREATE TABLE fact_transactions (

    transaction_key INTEGER PRIMARY KEY AUTOINCREMENT,

    investor_id INTEGER,

    fund_key INTEGER,

    date_key INTEGER,

    transaction_type TEXT,

    amount_inr REAL,

    kyc_status TEXT,

    state TEXT,

    FOREIGN KEY(fund_key)
    REFERENCES dim_fund(fund_key),

    FOREIGN KEY(date_key)
    REFERENCES dim_date(date_key)

);
""")

conn.commit()

print("fact_transactions created")


-- ======================================
-- Fact_performance Tables
-- ======================================
cursor.execute("DROP TABLE IF EXISTS fact_performance;")

cursor.execute("""
CREATE TABLE fact_performance (

    performance_key INTEGER PRIMARY KEY AUTOINCREMENT,

    fund_key INTEGER,

    return_1yr_pct REAL,

    return_3yr_pct REAL,

    return_5yr_pct REAL,

    benchmark_3yr_pct REAL,

    alpha REAL,

    beta REAL,

    sharpe_ratio REAL,

    sortino_ratio REAL,

    std_dev_ann_pct REAL,

    max_drawdown_pct REAL,

    FOREIGN KEY(fund_key)
    REFERENCES dim_fund(fund_key)

);
""")

conn.commit()

print("fact_performance created")


-- ======================================
-- Fact_aum Tables
-- ======================================
cursor.execute("DROP TABLE IF EXISTS fact_aum;")

cursor.execute("""
CREATE TABLE fact_aum (

    aum_key INTEGER PRIMARY KEY AUTOINCREMENT,

    fund_key INTEGER,

    date_key INTEGER,

    aum_crore REAL,

    FOREIGN KEY(fund_key)
    REFERENCES dim_fund(fund_key),

    FOREIGN KEY(date_key)
    REFERENCES dim_date(date_key)

);
""")

conn.commit()

print("fact_aum created")



-- ======================================
-- Star Schema  Tables
-- ======================================


cursor.executescript("""

DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_fund;


CREATE TABLE dim_fund (

    fund_key INTEGER PRIMARY KEY AUTOINCREMENT,

    amfi_code INTEGER UNIQUE,

    fund_house TEXT,

    scheme_name TEXT,

    category TEXT,

    sub_category TEXT,

    plan TEXT,

    launch_date DATE,

    benchmark TEXT,

    expense_ratio_pct REAL,

    exit_load_pct REAL,

    min_sip_amount REAL,

    min_lumpsum_amount REAL,

    fund_manager TEXT,

    risk_category TEXT,

    sebi_category_code TEXT

);


CREATE TABLE dim_date (

    date_key INTEGER PRIMARY KEY,

    full_date DATE,

    day INTEGER,

    month INTEGER,

    year INTEGER,

    quarter TEXT

);


CREATE TABLE fact_nav (

    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,

    fund_key INTEGER,

    date_key INTEGER,

    nav REAL,

    FOREIGN KEY(fund_key)
    REFERENCES dim_fund(fund_key),

    FOREIGN KEY(date_key)
    REFERENCES dim_date(date_key)

);

""")

conn.commit()

print("Star schema tables created")