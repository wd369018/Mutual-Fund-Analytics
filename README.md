# Mutual Fund Analytics

An end-to-end **Mutual Fund Analytics** project that performs data ingestion, cleaning, exploratory data analysis, SQL-based analytics, advanced performance analysis, and interactive Power BI dashboard visualization.

The project analyzes mutual fund schemes, NAV history, AUM, SIP inflows, investor transactions, portfolio holdings, benchmark indices, and fund performance metrics.

---

## 1. Project Overview

The objective of this project is to build a complete analytics pipeline for understanding mutual fund performance, investor behavior, risk, and market trends.

The project covers:

* Data ingestion and preprocessing
* Data cleaning and transformation
* Exploratory Data Analysis (EDA)
* SQL-based analytics
* Mutual fund performance analysis
* Risk and return analysis
* Sharpe and Sortino ratios
* Alpha and Beta analysis
* Maximum Drawdown
* Value at Risk (VaR) and Conditional VaR (CVaR)
* Rolling Sharpe Ratio
* Investor cohort analysis
* SIP continuity analysis
* Sector concentration using HHI
* Simple risk-based fund recommender
* Interactive Power BI dashboard

---

## 2. Project Architecture

```text
Mutual-Fund-Analytics/
│
├── data/
│   ├── raw/
│   │   └── Original CSV datasets
│   │
│   └── processed/
│       └── Cleaned and transformed datasets
│
├── notebooks/
│   ├── EDA notebooks
│   └── Advanced_Analytics.ipynb
│
├── scripts/
│   ├── data_ingestion.py
│   ├── live_nav_fetch.py
│   └── recommender.py
│
├── sql/
│   └── SQL analysis queries
│
├── dashboard/
│   ├── Power BI dashboard
│   ├── Dashboard.pdf
│   └── Dashboard screenshots
│
├── reports/
│   ├── Charts
│   ├── Analytics reports
│   └── Final project report
│
├── run_pipeline.py
├── requirements.txt
└── README.md
```

---

## 3. Technologies Used

* Python
* Pandas
* NumPy
* Matplotlib
* Plotly
* SQLite
* SQLAlchemy
* Jupyter Notebook
* Power BI
* Excel
* Git & GitHub

---

## 4. Dataset Description

The project uses 10 major datasets.

| Dataset                        | Description                                                                               |
| ------------------------------ | ----------------------------------------------------------------------------------------- |
| `01_fund_master.csv`           | Mutual fund scheme master information including AMC, category, benchmark and risk details |
| `02_nav_history.csv`           | Historical NAV data for mutual fund schemes                                               |
| `03_aum_by_fund_house.csv`     | Assets Under Management by fund house                                                     |
| `04_monthly_sip_inflows.csv`   | Monthly SIP inflow data                                                                   |
| `05_category_inflows.csv`      | Category-wise mutual fund inflows                                                         |
| `06_industry_folio_count.csv`  | Industry-level investor folio information                                                 |
| `07_scheme_performance.csv`    | Scheme-level performance and risk metrics                                                 |
| `08_investor_transactions.csv` | Investor transaction records including SIP, lumpsum and redemption transactions           |
| `09_portfolio_holdings.csv`    | Mutual fund portfolio and sector holdings                                                 |
| `10_benchmark_indices.csv`     | Benchmark index data used for performance comparison                                      |

---

## 5. Requirements

Make sure the following are installed:

* Python 3.10+
* Git
* Power BI Desktop
* Jupyter Notebook

Install Python dependencies using:

```bash
pip install -r requirements.txt
```

---

## 6. Setup Instructions

### Step 1 — Clone the Repository

```bash
git clone https://github.com/wd369018/Mutual-Fund-Analytics.git
```

Move into the project directory:

```bash
cd Mutual-Fund-Analytics
```

---

### Step 2 — Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 7. Running the ETL Pipeline

The project uses `run_pipeline.py` as the master execution script.

From the **project root directory**, run:

```bash
python run_pipeline.py
```

The pipeline performs the required data processing steps and generates cleaned/processed datasets.

The processed files are stored inside:

```text
data/processed/
```

### Important

Always execute the pipeline from the project root:

```text
Mutual-Fund-Analytics/
```

Do not run scripts using relative paths from inside the `scripts/` directory.

---

## 8. Running Individual Scripts

Individual scripts can also be executed when required.

Example:

```bash
python scripts/data_ingestion.py
```

For the NAV fetching script:

```bash
python scripts/live_nav_fetch.py
```

For the fund recommender:

```bash
python scripts/recommender.py
```

---

## 9. Exploratory Data Analysis

EDA notebooks are available inside:

```text
notebooks/
```

Open Jupyter Notebook:

```bash
jupyter notebook
```

Then open the required notebook and run the cells sequentially.

The EDA covers:

* Dataset structure
* Missing values
* Duplicate records
* NAV trends
* Fund category analysis
* AUM trends
* SIP inflows
* Investor transaction patterns
* Fund performance
* Risk-return relationships

---

## 10. Advanced Analytics

The project includes advanced mutual fund analytics such as:

### Performance Metrics

* CAGR
* Annualized return
* Sharpe Ratio
* Sortino Ratio
* Alpha
* Beta
* Maximum Drawdown

### Risk Analytics

* Historical VaR at 95% confidence
* CVaR
* Rolling 90-day Sharpe Ratio
* Risk-return analysis

### Investor Analytics

* Investor cohort analysis
* SIP continuity analysis
* At-risk SIP investor identification

### Portfolio Analytics

* Sector concentration
* Herfindahl-Hirschman Index (HHI)

### Fund Recommendation

A simple recommendation system ranks mutual funds according to investor risk appetite:

* Low
* Moderate
* High

The system returns the top-performing funds based on the selected risk category.

---

## 11. SQL Analytics

SQL queries are available inside:

```text
sql/
```

The project uses SQL/SQLite for structured analytical queries involving:

* Fund information
* NAV history
* Performance
* AUM
* Investor transactions
* Benchmark comparison

---

## 12. Power BI Dashboard

The project includes an interactive Power BI dashboard containing four major pages.

### Page 1 — Industry Overview

Includes:

* Total AUM
* SIP Inflows
* Total Folios
* Number of Schemes
* AUM trend
* AMC-wise AUM

### Page 2 — Fund Performance

Includes:

* Return vs Risk scatter plot
* Fund performance comparison
* Risk analysis
* Performance metrics

### Page 3 — Investor Analytics

Includes:

* Transaction analysis
* State-wise investor activity
* SIP/Lumpsum/Redemption analysis
* Investor behavior insights

### Page 4 — SIP & Market Trends

Includes:

* SIP inflow trends
* Benchmark/Nifty 50 comparison
* Market trend analysis

---

## 13. How to Open the Dashboard

Open the Power BI dashboard file located in:

```text
dashboard/
```

Open the `.pbix` file using **Microsoft Power BI Desktop**.

If a PDF version is available, it can be viewed directly:

```text
dashboard/Dashboard.pdf
```

Dashboard screenshots are also available in the `dashboard/` directory.

---

## 14. Project Outputs

The project generates several analytical outputs, including:

```text
data/processed/
reports/
dashboard/
```

Important outputs include:

* Cleaned datasets
* Performance reports
* VaR/CVaR report
* Rolling Sharpe chart
* Fund scorecard
* Investor cohort analysis
* SIP continuity analysis
* Fund recommendation results
* Power BI dashboard
* Dashboard screenshots
* Final project report

---

## 15. Key Analytical Insights

The project enables analysis of:

* Which mutual funds provide better risk-adjusted returns
* Relationship between fund return and volatility
* Mutual fund AUM growth
* SIP investment trends
* Investor transaction behavior
* Fund performance against benchmarks
* Portfolio sector concentration
* Investor SIP continuity
* Risk-adjusted fund rankings

---

## 16. Limitations

The analysis has the following limitations:

* Historical performance does not guarantee future returns.
* Dataset coverage depends on the available source data.
* Benchmark and risk-free-rate assumptions may affect performance metrics.
* Some investor-level insights depend on the completeness of transaction records.
* The recommendation system is a simple analytical model and should not be treated as financial advice.

---

## 17. Future Enhancements

Possible future improvements include:

* Real-time NAV updates
* Automated data refresh
* Machine learning-based fund recommendation
* Forecasting future NAV and AUM
* More advanced investor segmentation
* Cloud-based ETL pipeline
* Automated Power BI refresh
* Web-based dashboard deployment

---

## 18. How to Run the Complete Project

After cloning the repository:

```bash
cd Mutual-Fund-Analytics
```

Create and activate the virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the complete pipeline:

```bash
python run_pipeline.py
```

Then open the required notebooks from:

```text
notebooks/
```

Finally, open the Power BI dashboard from:

```text
dashboard/
```

---

## 19. Repository

GitHub Repository:

https://github.com/wd369018/Mutual-Fund-Analytics

---

## 20. Author

**Krishna Kumar Verma**

B.Tech Computer Science & Engineering (AI)

Mutual Fund Analytics — Data Analytics Capstone Project
