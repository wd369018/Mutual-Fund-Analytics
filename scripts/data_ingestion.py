"""
Data ingestion and ETL module for the Mutual Fund Analytics project.

Loads raw mutual-fund CSV datasets into the SQLite star schema.

Source files:
    01_fund_master.csv
    02_nav_history.csv
    03_aum_by_fund_house.csv
    07_scheme_performance.csv
    08_investor_transactions.csv
"""

from pathlib import Path
import logging
import sqlite3

import pandas as pd


# -------------------------------------------------------------------
# Project paths
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
DB_PATH = BASE_DIR / "database" / "bluestock_mf.db"


# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

def normalize_text(value):
    """Normalize text for reliable joins."""
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().split())


def normalize_key(value):
    """Create a normalized key for text matching."""
    return (
        normalize_text(value)
        .lower()
        .replace(".", "")
        .replace(",", "")
    )


def date_key_from_date(value):
    """Convert a date into YYYYMMDD integer date key."""
    if pd.isna(value):
        return None

    date = pd.to_datetime(value, errors="coerce")

    if pd.isna(date):
        return None

    return int(date.strftime("%Y%m%d"))


# -------------------------------------------------------------------
# Load source CSV files
# -------------------------------------------------------------------

def load_source_data():
    """Load required raw CSV datasets."""

    logger.info("Loading source CSV files...")

    files = {
        "fund_master": RAW_DIR / "01_fund_master.csv",
        "nav_history": RAW_DIR / "02_nav_history.csv",
        "aum": RAW_DIR / "03_aum_by_fund_house.csv",
        "performance": RAW_DIR / "07_scheme_performance.csv",
        "transactions": RAW_DIR / "08_investor_transactions.csv",
    }

    for name, path in files.items():
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

    fund_master = pd.read_csv(files["fund_master"])
    nav = pd.read_csv(files["nav_history"])
    aum = pd.read_csv(files["aum"])
    performance = pd.read_csv(files["performance"])
    transactions = pd.read_csv(files["transactions"])

    logger.info("Fund master rows: %s", len(fund_master))
    logger.info("NAV rows: %s", len(nav))
    logger.info("AUM rows: %s", len(aum))
    logger.info("Performance rows: %s", len(performance))
    logger.info("Transaction rows: %s", len(transactions))

    return (
        fund_master,
        nav,
        aum,
        performance,
        transactions,
    )


# -------------------------------------------------------------------
# Clean source data
# -------------------------------------------------------------------

def clean_data(
    fund_master,
    nav,
    aum,
    performance,
    transactions,
):
    """Clean and validate source datasets."""

    logger.info("Cleaning source data...")

    # ---------------------------------------------------------------
    # Fund master
    # ---------------------------------------------------------------

    fund_master["amfi_code"] = pd.to_numeric(
        fund_master["amfi_code"],
        errors="coerce",
    )

    fund_master = fund_master.dropna(
        subset=["amfi_code"]
    ).copy()

    fund_master["amfi_code"] = fund_master["amfi_code"].astype(int)

    fund_master["fund_house"] = (
        fund_master["fund_house"]
        .apply(normalize_text)
    )

    fund_master["scheme_name"] = (
        fund_master["scheme_name"]
        .apply(normalize_text)
    )

    fund_master["launch_date"] = pd.to_datetime(
        fund_master["launch_date"],
        errors="coerce",
    ).dt.strftime("%Y-%m-%d")

    # ---------------------------------------------------------------
    # NAV
    # ---------------------------------------------------------------

    nav["amfi_code"] = pd.to_numeric(
        nav["amfi_code"],
        errors="coerce",
    )

    nav["date"] = pd.to_datetime(
        nav["date"],
        errors="coerce",
    )

    nav["nav"] = pd.to_numeric(
        nav["nav"],
        errors="coerce",
    )

    nav = nav.dropna(
        subset=["amfi_code", "date", "nav"]
    ).copy()

    nav["amfi_code"] = nav["amfi_code"].astype(int)

    # ---------------------------------------------------------------
    # AUM
    # ---------------------------------------------------------------

    aum["date"] = pd.to_datetime(
        aum["date"],
        errors="coerce",
    )

    aum["fund_house"] = (
        aum["fund_house"]
        .apply(normalize_text)
    )

    aum["aum_crore"] = pd.to_numeric(
        aum["aum_crore"],
        errors="coerce",
    )

    aum["num_schemes"] = pd.to_numeric(
        aum["num_schemes"],
        errors="coerce",
    )

    aum = aum.dropna(
        subset=[
            "date",
            "fund_house",
            "aum_crore",
        ]
    ).copy()

    # ---------------------------------------------------------------
    # Performance
    # ---------------------------------------------------------------

    performance["amfi_code"] = pd.to_numeric(
        performance["amfi_code"],
        errors="coerce",
    )

    performance = performance.dropna(
        subset=["amfi_code"]
    ).copy()

    performance["amfi_code"] = (
        performance["amfi_code"].astype(int)
    )

    numeric_performance_columns = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
    ]

    for column in numeric_performance_columns:
        performance[column] = pd.to_numeric(
            performance[column],
            errors="coerce",
        )

    # ---------------------------------------------------------------
    # Transactions
    # ---------------------------------------------------------------

    transactions["investor_id"] = pd.to_numeric(
        transactions["investor_id"],
        errors="coerce",
    )

    transactions["amfi_code"] = pd.to_numeric(
        transactions["amfi_code"],
        errors="coerce",
    )

    transactions["transaction_date"] = pd.to_datetime(
        transactions["transaction_date"],
        errors="coerce",
    )

    transactions["amount_inr"] = pd.to_numeric(
        transactions["amount_inr"],
        errors="coerce",
    )

    transactions = transactions.dropna(
        subset=[
            "investor_id",
            "amfi_code",
            "transaction_date",
            "amount_inr",
        ]
    ).copy()

    transactions["investor_id"] = (
        transactions["investor_id"].astype(int)
    )

    transactions["amfi_code"] = (
        transactions["amfi_code"].astype(int)
    )

    logger.info("Cleaning completed successfully.")

    return (
        fund_master,
        nav,
        aum,
        performance,
        transactions,
    )


# -------------------------------------------------------------------
# Create database schema
# -------------------------------------------------------------------

def create_schema(conn):
    """Create the SQLite star-schema tables."""

    logger.info("Creating database schema...")

    conn.execute("PRAGMA foreign_keys = OFF")

    # Drop only ETL-managed tables.
    # Dependency order: facts first, dimensions afterwards.
    tables = [
        "fact_transactions",
        "fact_performance",
        "fact_nav",
        "fact_aum",
        "dim_fund_house",
        "dim_date",
        "dim_fund",
    ]

    for table in tables:
        conn.execute(f"DROP TABLE IF EXISTS {table}")

    # ---------------------------------------------------------------
    # dim_fund
    # ---------------------------------------------------------------

    conn.execute(
        """
        CREATE TABLE dim_fund (
            fund_key INTEGER PRIMARY KEY AUTOINCREMENT,
            amfi_code INTEGER UNIQUE NOT NULL,
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
        )
        """
    )

    # ---------------------------------------------------------------
    # dim_date
    # ---------------------------------------------------------------

    conn.execute(
        """
        CREATE TABLE dim_date (
            date_key INTEGER PRIMARY KEY,
            full_date DATE NOT NULL UNIQUE,
            day INTEGER,
            month INTEGER,
            year INTEGER,
            quarter TEXT
        )
        """
    )

    # ---------------------------------------------------------------
    # dim_fund_house
    # ---------------------------------------------------------------

    conn.execute(
        """
        CREATE TABLE dim_fund_house (
            fund_house_key INTEGER PRIMARY KEY AUTOINCREMENT,
            fund_house TEXT NOT NULL UNIQUE
        )
        """
    )

    # ---------------------------------------------------------------
    # fact_nav
    # ---------------------------------------------------------------

    conn.execute(
        """
        CREATE TABLE fact_nav (
            nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fund_key INTEGER NOT NULL,
            date_key INTEGER NOT NULL,
            nav REAL NOT NULL,
            FOREIGN KEY (fund_key)
                REFERENCES dim_fund(fund_key),
            FOREIGN KEY (date_key)
                REFERENCES dim_date(date_key)
        )
        """
    )

    # ---------------------------------------------------------------
    # fact_aum
    # ---------------------------------------------------------------

    conn.execute(
        """
        CREATE TABLE fact_aum (
            aum_key INTEGER PRIMARY KEY AUTOINCREMENT,
            fund_house_key INTEGER NOT NULL,
            date_key INTEGER NOT NULL,
            aum_crore REAL NOT NULL,
            num_schemes INTEGER,
            UNIQUE (fund_house_key, date_key),
            FOREIGN KEY (fund_house_key)
                REFERENCES dim_fund_house(fund_house_key),
            FOREIGN KEY (date_key)
                REFERENCES dim_date(date_key)
        )
        """
    )

    # ---------------------------------------------------------------
    # fact_performance
    # ---------------------------------------------------------------

    conn.execute(
        """
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
        )
        """
    )

    # ---------------------------------------------------------------
    # fact_transactions
    # ---------------------------------------------------------------

    conn.execute(
        """
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
        )
        """
    )

    conn.commit()

    logger.info("Database schema created successfully.")


# -------------------------------------------------------------------
# Load dimensions
# -------------------------------------------------------------------

def load_dimensions(
    conn,
    fund_master,
    nav,
    aum,
    transactions,
):
    """Load dimension tables."""

    logger.info("Loading dimension tables...")

    # ---------------------------------------------------------------
    # dim_fund
    # ---------------------------------------------------------------

    fund_columns = [
        "amfi_code",
        "fund_house",
        "scheme_name",
        "category",
        "sub_category",
        "plan",
        "launch_date",
        "benchmark",
        "expense_ratio_pct",
        "exit_load_pct",
        "min_sip_amount",
        "min_lumpsum_amount",
        "fund_manager",
        "risk_category",
        "sebi_category_code",
    ]

    fund_df = fund_master[fund_columns].drop_duplicates(
        subset=["amfi_code"]
    )

    fund_df.to_sql(
        "dim_fund",
        conn,
        if_exists="append",
        index=False,
    )

    # ---------------------------------------------------------------
    # dim_fund_house
    # ---------------------------------------------------------------

    house_values = (
        aum["fund_house"]
        .dropna()
        .drop_duplicates()
        .sort_values()
    )

    for house in house_values:
        conn.execute(
            """
            INSERT OR IGNORE INTO dim_fund_house (fund_house)
            VALUES (?)
            """,
            (house,),
        )

    # ---------------------------------------------------------------
    # dim_date
    #
    # IMPORTANT:
    # Use ALL dates from NAV, AUM and transactions.
    # Not just the 9 AUM dates.
    # ---------------------------------------------------------------

    all_dates = pd.concat(
        [
            nav["date"],
            aum["date"],
            transactions["transaction_date"],
        ],
        ignore_index=True,
    ).dropna().drop_duplicates()

    date_rows = []

    for date in sorted(all_dates):
        date = pd.Timestamp(date)

        date_rows.append(
            (
                int(date.strftime("%Y%m%d")),
                date.strftime("%Y-%m-%d"),
                int(date.day),
                int(date.month),
                int(date.year),
                f"Q{date.quarter}",
            )
        )

    conn.executemany(
        """
        INSERT INTO dim_date (
            date_key,
            full_date,
            day,
            month,
            year,
            quarter
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        date_rows,
    )

    conn.commit()

    logger.info(
        "dim_fund rows: %s",
        conn.execute(
            "SELECT COUNT(*) FROM dim_fund"
        ).fetchone()[0],
    )

    logger.info(
        "dim_fund_house rows: %s",
        conn.execute(
            "SELECT COUNT(*) FROM dim_fund_house"
        ).fetchone()[0],
    )

    logger.info(
        "dim_date rows: %s",
        conn.execute(
            "SELECT COUNT(*) FROM dim_date"
        ).fetchone()[0],
    )


# -------------------------------------------------------------------
# Build lookup dictionaries
# -------------------------------------------------------------------

def build_lookups(conn):
    """Build AMFI, date and fund-house lookup dictionaries."""

    fund_lookup = {
        int(row[1]): int(row[0])
        for row in conn.execute(
            """
            SELECT fund_key, amfi_code
            FROM dim_fund
            """
        )
    }

    date_lookup = {
        row[1]: int(row[0])
        for row in conn.execute(
            """
            SELECT date_key, full_date
            FROM dim_date
            """
        )
    }

    house_lookup = {
        normalize_key(row[1]): int(row[0])
        for row in conn.execute(
            """
            SELECT fund_house_key, fund_house
            FROM dim_fund_house
            """
        )
    }

    return fund_lookup, date_lookup, house_lookup


# -------------------------------------------------------------------
# Load fact tables
# -------------------------------------------------------------------

def load_fact_tables(
    conn,
    nav,
    aum,
    performance,
    transactions,
):
    """Load all fact tables."""

    logger.info("Loading fact tables...")

    fund_lookup, date_lookup, house_lookup = build_lookups(conn)

    # ---------------------------------------------------------------
    # fact_nav
    # ---------------------------------------------------------------

    nav_rows = []

    for row in nav.itertuples(index=False):

        fund_key = fund_lookup.get(int(row.amfi_code))

        if fund_key is None:
            continue

        date_string = pd.Timestamp(row.date).strftime("%Y-%m-%d")
        date_key = date_lookup.get(date_string)

        if date_key is None:
            continue

        nav_rows.append(
            (
                fund_key,
                date_key,
                float(row.nav),
            )
        )

    conn.executemany(
        """
        INSERT INTO fact_nav (
            fund_key,
            date_key,
            nav
        )
        VALUES (?, ?, ?)
        """,
        nav_rows,
    )

    logger.info("fact_nav rows inserted: %s", len(nav_rows))

    # ---------------------------------------------------------------
    # fact_aum
    # ---------------------------------------------------------------

    aum_rows = []

    for row in aum.itertuples(index=False):

        house_key = house_lookup.get(
            normalize_key(row.fund_house)
        )

        date_string = pd.Timestamp(row.date).strftime(
            "%Y-%m-%d"
        )

        date_key = date_lookup.get(date_string)

        if house_key is None or date_key is None:
            continue

        aum_rows.append(
            (
                house_key,
                date_key,
                float(row.aum_crore),
                int(row.num_schemes)
                if not pd.isna(row.num_schemes)
                else None,
            )
        )

    conn.executemany(
        """
        INSERT INTO fact_aum (
            fund_house_key,
            date_key,
            aum_crore,
            num_schemes
        )
        VALUES (?, ?, ?, ?)
        """,
        aum_rows,
    )

    logger.info("fact_aum rows inserted: %s", len(aum_rows))

    # ---------------------------------------------------------------
    # fact_performance
    # ---------------------------------------------------------------

    performance_rows = []

    performance_columns = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
    ]

    for row in performance.itertuples(index=False):

        fund_key = fund_lookup.get(int(row.amfi_code))

        if fund_key is None:
            continue

        values = []

        for column in performance_columns:
            value = getattr(row, column)

            if pd.isna(value):
                value = None
            else:
                value = float(value)

            values.append(value)

        performance_rows.append(
            (
                fund_key,
                *values,
            )
        )

    conn.executemany(
        """
        INSERT INTO fact_performance (
            fund_key,
            return_1yr_pct,
            return_3yr_pct,
            return_5yr_pct,
            benchmark_3yr_pct,
            alpha,
            beta,
            sharpe_ratio,
            sortino_ratio,
            std_dev_ann_pct,
            max_drawdown_pct
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        performance_rows,
    )

    logger.info(
        "fact_performance rows inserted: %s",
        len(performance_rows),
    )

    # ---------------------------------------------------------------
    # fact_transactions
    # ---------------------------------------------------------------

    transaction_rows = []

    for row in transactions.itertuples(index=False):

        fund_key = fund_lookup.get(int(row.amfi_code))

        date_string = pd.Timestamp(
            row.transaction_date
        ).strftime("%Y-%m-%d")

        date_key = date_lookup.get(date_string)

        if fund_key is None or date_key is None:
            continue

        transaction_rows.append(
            (
                int(row.investor_id),
                fund_key,
                date_key,
                normalize_text(row.transaction_type),
                float(row.amount_inr),
                normalize_text(row.kyc_status),
                normalize_text(row.state),
            )
        )

    conn.executemany(
        """
        INSERT INTO fact_transactions (
            investor_id,
            fund_key,
            date_key,
            transaction_type,
            amount_inr,
            kyc_status,
            state
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        transaction_rows,
    )

    logger.info(
        "fact_transactions rows inserted: %s",
        len(transaction_rows),
    )

    conn.commit()


# -------------------------------------------------------------------
# Validation
# -------------------------------------------------------------------

def validate_database(conn):
    """Validate final database row counts and relationships."""

    logger.info("Running database validation...")

    expected = {
        "dim_fund": 40,
        "dim_fund_house": 10,
        "fact_aum": 90,
        "fact_nav": 46000,
        "fact_performance": 40,
        "fact_transactions": 103419,
    }

    for table, expected_minimum in expected.items():

        count = conn.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        logger.info(
            "%-20s : %s rows",
            table,
            count,
        )

        if count == 0:
            raise RuntimeError(
                f"Validation failed: {table} is empty."
            )

    # ---------------------------------------------------------------
    # Validate AUM
    # ---------------------------------------------------------------

    aum_count = conn.execute(
        "SELECT COUNT(*) FROM fact_aum"
    ).fetchone()[0]

    if aum_count != 90:
        raise RuntimeError(
            f"Expected 90 AUM rows, found {aum_count}."
        )

    # ---------------------------------------------------------------
    # Validate foreign-key mappings
    # ---------------------------------------------------------------

    orphan_nav = conn.execute(
        """
        SELECT COUNT(*)
        FROM fact_nav f
        LEFT JOIN dim_fund d
            ON f.fund_key = d.fund_key
        WHERE d.fund_key IS NULL
        """
    ).fetchone()[0]

    if orphan_nav:
        raise RuntimeError(
            f"fact_nav contains {orphan_nav} orphan rows."
        )

    orphan_aum = conn.execute(
        """
        SELECT COUNT(*)
        FROM fact_aum f
        LEFT JOIN dim_fund_house h
            ON f.fund_house_key = h.fund_house_key
        LEFT JOIN dim_date d
            ON f.date_key = d.date_key
        WHERE h.fund_house_key IS NULL
           OR d.date_key IS NULL
        """
    ).fetchone()[0]

    if orphan_aum:
        raise RuntimeError(
            f"fact_aum contains {orphan_aum} orphan rows."
        )

    orphan_transactions = conn.execute(
        """
        SELECT COUNT(*)
        FROM fact_transactions f
        LEFT JOIN dim_fund d
            ON f.fund_key = d.fund_key
        LEFT JOIN dim_date dt
            ON f.date_key = dt.date_key
        WHERE d.fund_key IS NULL
           OR dt.date_key IS NULL
        """
    ).fetchone()[0]

    if orphan_transactions:
        raise RuntimeError(
            f"fact_transactions contains "
            f"{orphan_transactions} orphan rows."
        )

    logger.info("Database validation passed successfully.")


# -------------------------------------------------------------------
# Main ETL entry point
# -------------------------------------------------------------------

def main():
    """Run the complete data ingestion and database loading process."""

    logger.info("Starting data ingestion...")

    (
        fund_master,
        nav,
        aum,
        performance,
        transactions,
    ) = load_source_data()

    (
        fund_master,
        nav,
        aum,
        performance,
        transactions,
    ) = clean_data(
        fund_master,
        nav,
        aum,
        performance,
        transactions,
    )

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = sqlite3.connect(DB_PATH)

    try:
        create_schema(conn)

        load_dimensions(
            conn,
            fund_master,
            nav,
            aum,
            transactions,
        )

        load_fact_tables(
            conn,
            nav,
            aum,
            performance,
            transactions,
        )

        validate_database(conn)

        logger.info(
            "Data ingestion completed successfully."
        )

    except Exception:
        conn.rollback()
        logger.exception(
            "Data ingestion failed."
        )
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    main()