"""
compute_metrics.py
==================

Performance-metrics script extracted/cleaned from Performance_Analytics.ipynb.

Calculates the core D4 metrics used in the notebook:
- Daily returns
- 1Y / 3Y / 5Y CAGR
- Annualized volatility
- Sharpe Ratio
- Sortino Ratio
- NIFTY100 benchmark returns
- Alpha and Beta
- Maximum Drawdown

The script uses project-relative paths (pathlib) instead of Colab /content paths.

Expected input:
    data/processed/Cleaned_02_nav_history.csv
    data/processed/10_benchmark_indices.csv

Generated outputs:
    data/processed/daily_returns.csv
    data/processed/alpha_beta_results.csv
    data/processed/maximum_drawdown_report.csv
    data/processed/performance_metrics.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import linregress


# ---------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

NAV_FILE = PROCESSED_DIR / "Cleaned_02_nav_history.csv"
BENCHMARK_FILE = PROCESSED_DIR / "10_benchmark_indices.csv"

DAILY_RETURNS_FILE = PROCESSED_DIR / "daily_returns.csv"
ALPHA_BETA_FILE = PROCESSED_DIR / "alpha_beta_results.csv"
DRAWDOWN_FILE = PROCESSED_DIR / "maximum_drawdown_report.csv"
PERFORMANCE_FILE = PROCESSED_DIR / "performance_metrics.csv"

TRADING_DAYS = 252
RISK_FREE_RATE = 0.065


# ---------------------------------------------------------------------
# Data loading / validation
# ---------------------------------------------------------------------

def load_nav_data() -> pd.DataFrame:
    """Load and prepare NAV history using the notebook's columns."""
    if not NAV_FILE.exists():
        raise FileNotFoundError(f"NAV file not found: {NAV_FILE}")

    nav = pd.read_csv(NAV_FILE)

    required = {"amfi_code", "date", "nav"}
    missing = required - set(nav.columns)
    if missing:
        raise ValueError(
            f"NAV file is missing required columns: {sorted(missing)}"
        )

    nav["date"] = pd.to_datetime(nav["date"], errors="coerce")
    nav["nav"] = pd.to_numeric(nav["nav"], errors="coerce")
    nav["amfi_code"] = pd.to_numeric(nav["amfi_code"], errors="coerce")

    nav = nav.dropna(subset=["amfi_code", "date", "nav"])
    nav = nav[nav["nav"] > 0].copy()

    nav = nav.sort_values(["amfi_code", "date"])
    nav = nav.drop_duplicates(
        subset=["amfi_code", "date"],
        keep="last",
    )

    # Same calculation used in the notebook.
    nav["daily_return"] = (
        nav.groupby("amfi_code")["nav"].pct_change()
    )

    return nav


def load_benchmark_data() -> pd.DataFrame:
    """Load NIFTY100 benchmark data and calculate daily benchmark returns."""
    if not BENCHMARK_FILE.exists():
        raise FileNotFoundError(
            f"Benchmark file not found: {BENCHMARK_FILE}"
        )

    benchmark = pd.read_csv(BENCHMARK_FILE)

    required = {"date", "index_name", "close_value"}
    missing = required - set(benchmark.columns)
    if missing:
        raise ValueError(
            "Benchmark file is missing required columns: "
            f"{sorted(missing)}"
        )

    benchmark["date"] = pd.to_datetime(
        benchmark["date"], errors="coerce"
    )
    benchmark["close_value"] = pd.to_numeric(
        benchmark["close_value"], errors="coerce"
    )

    benchmark = benchmark.dropna(
        subset=["date", "close_value"]
    ).copy()

    benchmark = benchmark[
        benchmark["index_name"].astype(str).str.upper().eq("NIFTY100")
    ].copy()

    if benchmark.empty:
        raise ValueError("No NIFTY100 observations found in benchmark data.")

    benchmark = benchmark.sort_values("date")
    benchmark = benchmark.drop_duplicates(
        subset=["date"], keep="last"
    )

    # Same formula used in the notebook:
    # (close / previous close) - 1
    benchmark["benchmark_return"] = (
        benchmark["close_value"]
        / benchmark["close_value"].shift(1)
    ) - 1

    return benchmark[
        ["date", "index_name", "close_value", "benchmark_return"]
    ]


# ---------------------------------------------------------------------
# CAGR
# ---------------------------------------------------------------------

def calculate_cagr(group: pd.DataFrame, years: int) -> float:
    """
    Calculate CAGR exactly in the notebook's date-based manner.

    The notebook:
        end_date = max(date)
        start_date = end_date - DateOffset(years=years)
        start_data = rows with date >= start_date, first row
        end_data = last row
        CAGR = (end_nav / start_nav) ** (1 / years) - 1
    """
    group = group.sort_values("date")

    end_date = group["date"].max()
    start_date = end_date - pd.DateOffset(years=years)

    start_data = group[group["date"] >= start_date].head(1)
    end_data = group.tail(1)

    if start_data.empty or end_data.empty:
        return np.nan

    start_nav = float(start_data["nav"].iloc[0])
    end_nav = float(end_data["nav"].iloc[0])

    if start_nav <= 0 or end_nav <= 0:
        return np.nan

    return (end_nav / start_nav) ** (1 / years) - 1


def calculate_cagr_table(nav: pd.DataFrame) -> pd.DataFrame:
    """Create the notebook's 1Y/3Y/5Y CAGR comparison table."""
    records = []

    for amfi_code, group in nav.groupby("amfi_code"):
        records.append(
            {
                "amfi_code": int(amfi_code),
                "CAGR_1Y": calculate_cagr(group, 1) * 100,
                "CAGR_3Y": calculate_cagr(group, 3) * 100,
                "CAGR_5Y": calculate_cagr(group, 5) * 100,
            }
        )

    return pd.DataFrame(records)


# ---------------------------------------------------------------------
# Sharpe / Sortino / volatility
# ---------------------------------------------------------------------

def calculate_sharpe_table(nav: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate annualized Sharpe Ratio using the notebook's exact formula:

        ((avg_daily_return * 252) - 0.065)
        / (std_daily_return * sqrt(252))
    """
    returns = nav.dropna(subset=["daily_return"]).copy()

    sharpe_table = (
        returns.groupby("amfi_code")
        .agg(
            avg_daily_return=("daily_return", "mean"),
            std_daily_return=("daily_return", "std"),
        )
        .reset_index()
    )

    sharpe_table["Sharpe_Ratio"] = (
        (
            sharpe_table["avg_daily_return"] * TRADING_DAYS
            - RISK_FREE_RATE
        )
        / (
            sharpe_table["std_daily_return"]
            * np.sqrt(TRADING_DAYS)
        )
    )

    sharpe_table["std_dev_ann_pct"] = (
        sharpe_table["std_daily_return"]
        * np.sqrt(TRADING_DAYS)
        * 100
    )

    return sharpe_table


def calculate_sortino(group: pd.DataFrame) -> float:
    """Calculate Sortino using the notebook's downside-return method."""
    excess_return = group["daily_return"] - (
        RISK_FREE_RATE / TRADING_DAYS
    )

    downside_returns = excess_return[
        excess_return < 0
    ]

    downside_std = downside_returns.std()

    if downside_std == 0 or pd.isna(downside_std):
        return np.nan

    sortino = (
        excess_return.mean()
        / downside_std
    ) * np.sqrt(TRADING_DAYS)

    return sortino


def calculate_sortino_table(nav: pd.DataFrame) -> pd.DataFrame:
    """Calculate Sortino Ratio for every fund."""
    returns = nav.dropna(subset=["daily_return"]).copy()

    result = (
        returns.groupby("amfi_code")
        .apply(calculate_sortino)
        .reset_index()
    )

    result.columns = ["amfi_code", "sortino_ratio"]
    return result


# ---------------------------------------------------------------------
# Alpha / Beta
# ---------------------------------------------------------------------

def calculate_alpha_beta(
    nav: pd.DataFrame,
    benchmark: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate Alpha and Beta against NIFTY100 using scipy linregress,
    matching the notebook:

        linregress(benchmark_return, daily_return)
        beta  = slope
        alpha = intercept * 252
    """
    merged = nav.merge(
        benchmark[["date", "benchmark_return"]],
        on="date",
        how="inner",
    )

    alpha_beta = []

    for code in merged["amfi_code"].dropna().unique():
        fund = merged[merged["amfi_code"] == code].copy()

        fund = fund.dropna(
            subset=["daily_return", "benchmark_return"]
        )

        # The notebook calculates Alpha/Beta only when enough
        # observations are available.
        if len(fund) <= 30:
            alpha_beta.append(
                {
                    "amfi_code": int(code),
                    "alpha": np.nan,
                    "beta": np.nan,
                }
            )
            continue

        result = linregress(
            fund["benchmark_return"],
            fund["daily_return"],
        )

        alpha_beta.append(
            {
                "amfi_code": int(code),
                "alpha": result.intercept * TRADING_DAYS,
                "beta": result.slope,
            }
        )

    return pd.DataFrame(alpha_beta)


# ---------------------------------------------------------------------
# Maximum Drawdown
# ---------------------------------------------------------------------

def calculate_drawdown(nav: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate running maximum, drawdown and maximum drawdown.

    Notebook logic:
        running_max = NAV cumulative maximum
        drawdown = NAV / running_max - 1
        maximum_drawdown = minimum drawdown
    """
    result = nav.copy()

    result["running_max"] = (
        result.groupby("amfi_code")["nav"].cummax()
    )

    result["drawdown"] = (
        result["nav"] / result["running_max"]
    ) - 1

    maximum_drawdown = (
        result.groupby("amfi_code")["drawdown"]
        .min()
        .reset_index()
    )

    maximum_drawdown.columns = [
        "amfi_code",
        "maximum_drawdown",
    ]

    return result, maximum_drawdown


# ---------------------------------------------------------------------
# Daily returns output
# ---------------------------------------------------------------------

def save_daily_returns(nav: pd.DataFrame) -> None:
    """Save the daily-return dataset used by the notebook."""
    output = nav[
        ["amfi_code", "date", "nav", "daily_return"]
    ].copy()

    output.to_csv(
        DAILY_RETURNS_FILE,
        index=False,
    )


# ---------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------

def main() -> None:
    """Run all D4 performance calculations and save CSV outputs."""
    print("=" * 70)
    print("MUTUAL FUND PERFORMANCE METRICS")
    print("=" * 70)

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\n[1/6] Loading NAV history...")
    nav = load_nav_data()
    print(f"      Records: {len(nav):,}")
    print(f"      Funds:   {nav['amfi_code'].nunique()}")

    print("\n[2/6] Loading NIFTY100 benchmark...")
    benchmark = load_benchmark_data()
    print(f"      Benchmark records: {len(benchmark):,}")

    print("\n[3/6] Calculating daily returns + CAGR...")
    save_daily_returns(nav)

    cagr_table = calculate_cagr_table(nav)

    print("\n[4/6] Calculating Sharpe + Sortino...")
    sharpe_table = calculate_sharpe_table(nav)
    sortino_table = calculate_sortino_table(nav)

    print("\n[5/6] Calculating Alpha + Beta...")
    alpha_beta_table = calculate_alpha_beta(
        nav,
        benchmark,
    )

    alpha_beta_table.to_csv(
        ALPHA_BETA_FILE,
        index=False,
    )

    print("\n[6/6] Calculating Maximum Drawdown...")
    nav_with_drawdown, drawdown_table = calculate_drawdown(nav)

    drawdown_table.to_csv(
        DRAWDOWN_FILE,
        index=False,
    )

    # Main D4 performance table.
    performance_metrics = (
        cagr_table
        .merge(
            sharpe_table[
                [
                    "amfi_code",
                    "avg_daily_return",
                    "std_daily_return",
                    "Sharpe_Ratio",
                    "std_dev_ann_pct",
                ]
            ],
            on="amfi_code",
            how="left",
        )
        .merge(
            sortino_table,
            on="amfi_code",
            how="left",
        )
        .merge(
            alpha_beta_table,
            on="amfi_code",
            how="left",
        )
        .merge(
            drawdown_table,
            on="amfi_code",
            how="left",
        )
    )

    # Percentage form is kept for readability where appropriate.
    performance_metrics["maximum_drawdown_pct"] = (
        performance_metrics["maximum_drawdown"] * 100
    )

    performance_metrics.to_csv(
        PERFORMANCE_FILE,
        index=False,
    )

    print("\nFiles created:")
    print(f"  ✓ {DAILY_RETURNS_FILE}")
    print(f"  ✓ {ALPHA_BETA_FILE}")
    print(f"  ✓ {DRAWDOWN_FILE}")
    print(f"  ✓ {PERFORMANCE_FILE}")

    print("\nPerformance metrics completed successfully.")


if __name__ == "__main__":
    main()
