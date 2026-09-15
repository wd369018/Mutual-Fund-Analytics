# Data Dictionary — Mutual Fund Analytics Project

## Overview
This project performs end-to-end analytics on mutual fund data, including data ingestion, cleaning, exploratory data analysis, SQL-based analytics, performance metrics, and risk analysis. The data is stored in a SQLite star schema database (`bluestock_mf.db`).

---

## 1. Dimension Tables

### `dim_fund`
Contains master information about each mutual fund scheme.

| Column | Data Type | Business Definition | Source |
|--------|-----------|---------------------|--------|
| `fund_key` | INTEGER | Primary key, auto-generated identifier for each fund | ETL-generated |
| `amfi_code` | INTEGER | Unique AMFI (Association of Mutual Funds in India) code identifying the fund scheme | `01_fund_master.csv` |
| `fund_house` | TEXT | Name of the Asset Management Company (AMC) offering the fund | `01_fund_master.csv` |
| `scheme_name` | TEXT | Name of the mutual fund scheme | `01_fund_master.csv` |
| `category` | TEXT | Broad investment category (Equity, Debt) | `01_fund_master.csv` |
| `sub_category` | TEXT | Specific sub-category within the main category (e.g., Large Cap, Mid Cap, Gilt) | `01_fund_master.csv` |
| `plan` | TEXT | Plan type (Regular or Direct) | `01_fund_master.csv` |
| `launch_date` | DATE | Date when the fund scheme was launched | `01_fund_master.csv` |
| `benchmark` | TEXT | Benchmark index used for performance comparison (e.g., NIFTY 100 TRI) | `01_fund_master.csv` |
| `expense_ratio_pct` | REAL | Annual expense ratio percentage charged by the fund | `01_fund_master.csv` |
| `exit_load_pct` | REAL | Exit load percentage charged if units are redeemed before a certain period | `01_fund_master.csv` |
| `min_sip_amount` | INTEGER | Minimum SIP (Systematic Investment Plan) amount in INR | `01_fund_master.csv` |
| `min_lumpsum_amount` | INTEGER | Minimum lump-sum investment amount in INR | `01_fund_master.csv` |
| `fund_manager` | TEXT | Name of the fund manager responsible for the scheme | `01_fund_master.csv` |
| `risk_category` | TEXT | Categorical risk level (Low, Moderate, Moderately High, High, Very High) | `01_fund_master.csv` |
| `sebi_category_code` | TEXT | SEBI-mandated category code for the fund | `01_fund_master.csv` |

**Unique Counts:** 40 funds, 10 fund houses

---

### `dim_date`
Contains a calendar date dimension used for time-based analysis.

| Column | Data Type | Business Definition | Source |
|--------|-----------|---------------------|--------|
| `date_key` | INTEGER | Surrogate key in YYYYMMDD format (e.g., 20220103) | ETL-generated |
| `full_date` | DATE | Complete date in YYYY-MM-DD format | ETL-generated |
| `day` | INTEGER | Day of the month (1-31) | ETL-generated |
| `month` | INTEGER | Month of the year (1-12) | ETL-generated |
| `year` | INTEGER | Year (e.g., 2022) | ETL-generated |
| `quarter` | TEXT | Quarter of the year (Q1, Q2, Q3, Q4) | ETL-generated |

**Unique Count:** 1,296 date keys covering the range of transaction and NAV data

---

### `dim_fund_house` (implicit in schema)
Fund houses are represented as rows in `dim_fund` via `fund_house` column, with 10 unique fund houses:
- Aditya Birla Sun Life MF
- Axis Mutual Fund
- DSP Mutual Fund
- HDFC Mutual Fund
- ICICI Prudential MF
- Kotak Mahindra MF
- Mirae Asset MF
- Nippon India MF
- SBI Mutual Fund
- UTI Mutual Fund

---

## 2. Fact Tables

### `fact_nav`
Contains daily NAV (Net Asset Value) history for all funded schemes.

| Column | Data Type | Business Definition | Source |
|--------|-----------|---------------------|--------|
| `nav_id` | INTEGER | Primary key, auto-generated | ETL-generated |
| `fund_key` | INTEGER | Foreign key referencing `dim_fund.fund_key` | `02_nav_history.csv` |
| `date_key` | INTEGER | Foreign key referencing `dim_date.date_key` | `02_nav_history.csv` |
| `nav` | REAL | Net Asset Value per unit on the given date | `02_nav_history.csv` |

**Row Count:** 46,000 records across 40 funds  
**Date Range:** 2022-01-03 to 2026-05-29  
**Validation:** NAV > 0 enforced; duplicates removed (keep last per amfi_code + date)

---

### `fact_aum`
Contains Assets Under Management (AUM) by fund house over time.

| Column | Data Type | Business Definition | Source |
|--------|-----------|---------------------|--------|
| `aum_key` | INTEGER | Primary key, auto-generated | ETL-generated |
| `fund_house_key` | INTEGER | Foreign key referencing `dim_fund.fund_key` | `03_aum_by_fund_house.csv` |
| `date_key` | INTEGER | Foreign key referencing `dim_date.date_key` | `03_aum_by_fund_house.csv` |
| `aum_crore` | REAL | AUM in crores of Indian Rupees | `03_aum_by_fund_house.csv` |
| `num_schemes` | INTEGER | Number of schemes offered by the fund house | `03_aum_by_fund_house.csv` |

**Row Count:** 8 records (mapped to first fund key per fund house due to schema design)  
**Note:** Schema links `fund_house_key` to `dim_fund.fund_key`; each fund house has multiple funds

---

### `fact_performance`
Contains scheme-level performance and risk metrics.

| Column | Data Type | Business Definition | Source |
|--------|-----------|---------------------|--------|
| `performance_key` | INTEGER | Primary key, auto-generated | ETL-generated |
| `fund_key` | INTEGER | Foreign key referencing `dim_fund.fund_key` | `07_scheme_performance.csv` |
| `return_1yr_pct` | REAL | 1-year return percentage | `07_scheme_performance.csv` |
| `return_3yr_pct` | REAL | 3-year return percentage | `07_scheme_performance.csv` |
| `return_5yr_pct` | REAL | 5-year return percentage | `07_scheme_performance.csv` |
| `benchmark_3yr_pct` | REAL | 3-year benchmark index return percentage | `07_scheme_performance.csv` |
| `alpha` | REAL | Alpha metric (excess return over benchmark) | `07_scheme_performance.csv` |
| `beta` | REAL | Beta metric (volatility relative to benchmark) | `07_scheme_performance.csv` |
| `sharpe_ratio` | REAL | Sharpe ratio (risk-adjusted return) | `07_scheme_performance.csv` |
| `sortino_ratio` | REAL | Sortino ratio (downside-risk-adjusted return) | `07_scheme_performance.csv` |
| `std_dev_ann_pct` | REAL | Annualized standard deviation percentage | `07_scheme_performance.csv` |
| `max_drawdown_pct` | REAL | Maximum drawdown percentage over the measurement period | `07_scheme_performance.csv` |

**Row Count:** 40 records (one per fund)  
**Validation:** All return values validated as numeric; expense ratio range checked (0.1% – 2.5%)

---

### `fact_transactions`
Contains investor transaction records (SIP, Lumpsum, Redemption).

| Column | Data Type | Business Definition | Source |
|--------|-----------|---------------------|--------|
| `transaction_key` | INTEGER | Primary key, auto-generated | ETL-generated |
| `investor_id` | INTEGER | Unique identifier for the investor (mapped from string IDs) | `08_investor_transactions.csv` |
| `fund_key` | INTEGER | Foreign key referencing `dim_fund.fund_key` | `08_investor_transactions.csv` |
| `date_key` | INTEGER | Foreign key referencing `dim_date.date_key` | `08_investor_transactions.csv` |
| `transaction_type` | TEXT | Type of transaction: SIP, Lumpsum, or Redemption | `08_investor_transactions.csv` |
| `amount_inr` | REAL | Transaction amount in Indian Rupees | `08_investor_transactions.csv` |
| `kyc_status` | Text | KYC verification status: Verified, Pending | `08_investor_transactions.csv` |
| `state` | TEXT | Investor's state of residence | `08_investor_transactions.csv` |

**Row Count:** 32,778 records  
**Transaction Types:** SIP (19,716), Lumpsum (8,095), Redemption (4,967)  
**KYC Status:** Verified (30,146), Pending (2,632)  
**Date Range:** 2024-01-01 to 2025-05-30

---

## 3. Cleaned CSV Datasets (in `data/processed/`)

| File | Description | Row Count |
|------|-------------|-----------|
| `Cleaned_01_data_fund_master.csv` | Cleaned fund master with normalized text fields | 40 |
| `Cleaned_02_nav_history.csv` | Cleaned NAV history with parsed dates, forward-filled missing values, duplicates removed | 46,000 |
| `Cleaned_03_aum_by_fund_house.csv` | Cleaned AUM data by fund house | 90 |
| `Cleaned_04_monthly_sip_inflows.csv` | Monthly SIP inflow statistics | 48 |
| `Cleaned_05_category_inflows.csv` | Category-wise mutual fund inflows | 144 |
| `Cleaned_06_industry_folio_count.csv` | Industry-level folio count data | 21 |
| `Cleaned_07_scheme_performance.csv` | Scheme-level performance and risk metrics | 40 |
| `Cleaned_08_investor_transactions.csv` | Cleaned investor transactions with standardized types | 32,778 |
| `Cleaned_10_benchmark_indices.csv` | Benchmark index data (NIFTY100) | 8,050 |
| `live_nav_api.csv` | Live NAV fetched from mfapi.in API | 3,164 |

---

## 4. Data Quality & Anomaly Notes

### `01_fund_master.csv`
- AMFI codes range from 100016 to 149324, with 40 unique codes
- Expense ratios range from 0.55% to 1.64% (all within expected 0.1% – 2.5% range)
- Risk categories: Low (6), Moderate (16), High (8), Very High (6), Moderately High (4)
- 10 unique fund houses covering both Equity and Debt categories

### `02_nav_history.csv`
- 46,000 NAV records across 40 funds
- Dates forward-filled for holidays/weekends
- Duplicate records removed (keep last per amfi_code + date)
- All NAV values validated > 0

### `07_scheme_performance.csv`
- 40 schemes with complete performance data
- Return metrics: 1Y (5.43% – 23.80%), 3Y, 5Y
- Sharpe ratios: 0.80 – 7.68
- Max drawdowns: -33.50% to -2.23%
- All expense ratios within valid range (0.55% – 1.64%)

### `08_investor_transactions.csv`
- 32,778 transaction records
- Transaction types standardized to: SIP, Lumpsum, Redemption
- Amounts validated > 0
- Dates parsed to datetime format
- KYC status standardized: Verified, Pending

---

## 5. Database Schema (SQLite Star Schema)

The database uses a star schema with 6 tables:
- **Dimension tables:** `dim_fund`, `dim_date`
- **Fact tables:** `fact_nav`, `fact_aum`, `fact_performance`, `fact_transactions`

**Relationships:**
- `fact_nav.fund_key` → `dim_fund.fund_key` (many-to-one)
- `fact_nav.date_key` → `dim_date.date_key` (many-to-one)
- `fact_aum.fund_house_key` → `dim_fund.fund_key` (many-to-one)
- `fact_aum.date_key` → `dim_date.date_key` (many-to-one)
- `fact_performance.fund_key` → `dim_fund.fund_key` (many-to-one)
- `fact_transactions.fund_key` → `dim_fund.fund_key` (many-to-one)
- `fact_transactions.date_key` → `dim_date.date_key` (many-to-one)
- `fact_transactions.investor_id` → investor identifier (many-to-one)

---

## 6. Analytical SQL Queries (in `sql/queries.sql`)

The project includes 10+ analytical SQL queries:

1. **Top 5 Schemes by AUM** - Identify the largest schemes by assets
2. **Average NAV per Month** - Track average NAV trends over time
3. **SIP Investment YOY Growth** - Year-over-year growth in SIP investments
4. **Transactions by State** - Geographic distribution of investor activity
5. **Funds with Expense Ratio < 1%** - Identify low-cost funds
6. **Top 5 Schemes by 5-Year Return** - Highest returning funds
7. **Total Investment by Fund Category** - Category-wise investment analysis
8. **Transactions by Year and Month** - Monthly transaction trends
9. **Top 10 Schemes by Highest NAV** - Largest NAV funds
9. **Number of Funds by Risk Category** - Risk distribution across funds

Each query uses standard SQL with JOINs between fact and dimension tables, GROUP BY clauses, and aggregate functions (COUNT, SUM, AVG, ROUND, LAG for YoY calculations).

---

## 7. ETL Pipeline

The data ingestion pipeline (`scripts/data_ingestion.py`) performs the following steps:

1. **Load Source CSVs** - Read 10 raw CSV datasets from `data/raw/`
2. **Clean Data** - Normalize text, parse dates, convert types, validate constraints
3. **Create Schema** - Drop and recreate SQLite star schema tables
4. **Load Dimensions** - Populate `dim_fund`, `dim_date`, `dim_fund_house`
5. **Load Fact Tables** - Populate `fact_nav`, `fact_aum`, `fact_performance`, `fact_transactions`
6. **Validate Database** - Check row counts, foreign key integrity, orphan records

The pipeline is executed via `run_pipeline.py` from the project root directory.

---

## 8. Dependencies

- **Python 3.10+**
- **Pandas** (3.0.5) - Data manipulation and cleaning
- **NumPy** (2.5.1) - Numerical operations
- **Matplotlib** (3.11.1) - Charting
- **Seaborn** (0.13.2) - Statistical visualizations
- **Plotly** (6.9.0) - Interactive plots
- **SQLAlchemy** (2.0.51) - Database abstraction
- **SciPy** (1.18.0) - Statistical functions (linregress for Alpha/Beta)
- **Requests** (2.34.2) - API calls for live NAV fetching
- **Jupyter** (7.6.1) - Notebook interface

---

*Data Dictionary generated for Day 2: Cleaned data + SQLite DB loaded*