-- ======================================
-- Star Schema for Mutual Fund Analytics
-- ======================================

-- Drop tables if they exist (in dependency order: facts first, dimensions afterwards)
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_fund;

-- ======================================
-- dim_fund
-- ======================================

CREATE TABLE dim_fund (
    fund_key INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER UNIQUE NOT NULL,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
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

-- ======================================
-- dim_date
-- ======================================

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day INTEGER,
    month INTEGER,
    year INTEGER,
    quarter TEXT
);

-- ======================================
-- fact_nav
-- ======================================

CREATE TABLE fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    nav REAL NOT NULL,
    FOREIGN KEY (fund_key)
        REFERENCES dim_fund(fund_key),
    FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
);

-- ======================================
-- fact_aum
-- ======================================

CREATE TABLE fact_aum (
    aum_key INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    aum_crore REAL NOT NULL,
    num_schemes INTEGER,
    UNIQUE (fund_house_key, date_key),
    FOREIGN KEY (fund_house_key)
        REFERENCES dim_fund(fund_key),
    FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
);

-- ======================================
-- fact_performance
-- ======================================

CREATE TABLE fact_performance (
    performance_key INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_key INTEGER NOT NULL,
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
    FOREIGN KEY (fund_key)
        REFERENCES dim_fund(fund_key)
);

-- ======================================
-- fact_transactions
-- ======================================

CREATE TABLE fact_transactions (
    transaction_key INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id INTEGER NOT NULL,
    fund_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    transaction_type TEXT,
    amount_inr REAL,
    kyc_status TEXT,
    state TEXT,
    FOREIGN KEY (fund_key)
        REFERENCES dim_fund(fund_key),
    FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
);