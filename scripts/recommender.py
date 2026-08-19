"""
Mutual-fund recommendation module.

This script ranks mutual funds based on risk-adjusted
performance metrics and generates recommendations.
"""


import pandas as pd
import os
from pathlib import Path



# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

FUND_MASTER_PATH = PROCESSED_DIR / "Cleaned_01_data_fund_master.csv"
PERFORMANCE_PATH = PROCESSED_DIR / "Cleaned_07_scheme_performance (1) (1).csv"


# ============================================================
# 2. LOAD DATA
# ============================================================

def load_data():

    fund_master = pd.read_csv(FUND_MASTER_PATH)
    performance = pd.read_csv(PERFORMANCE_PATH)

    return fund_master, performance


# ============================================================
# 3. PREPARE DATA
# ============================================================

def prepare_data(fund_master, performance):

    # Merge fund information with performance metrics
    df = pd.merge(
        fund_master,
        performance,
        on="amfi_code",
        how="inner",
        suffixes=('_master', '_performance') # Add suffixes to distinguish common columns
    )

    # Remove duplicate funds if any
    df = df.drop_duplicates(subset=["amfi_code"])

    return df


# ============================================================
# 4. NORMALIZE VALUES
# ============================================================

def normalize(series):

    series = pd.to_numeric(series, errors="coerce")

    min_value = series.min()
    max_value = series.max()

    if max_value == min_value:
        return pd.Series(1, index=series.index)

    return (series - min_value) / (max_value - min_value)


# ============================================================
# 5. CALCULATE FUND SCORE
# ============================================================

def calculate_score(df):

   

    # Make sure numerical columns are numeric
    numeric_columns = [
        "return_3yr_pct",
        "sharpe_ratio",
        "alpha",
        "expense_ratio_pct_performance",
        "max_drawdown_pct"
    ]

    for column in numeric_columns:

        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # Positive factors
    # Higher value = better
    # --------------------------------------------------------

    df["return_score"] = normalize(df["return_3yr_pct"])

    df["sharpe_score"] = normalize(df["sharpe_ratio"])

    df["alpha_score"] = normalize(df["alpha"])


    # --------------------------------------------------------
    # Negative factors
    # Lower value = better
    # --------------------------------------------------------

    df["expense_score"] = 1 - normalize(
        df["expense_ratio_pct_performance"]
    )

    df["drawdown_score"] = 1 - normalize(
        abs(df["max_drawdown_pct"])
    )


    # --------------------------------------------------------
    # Composite Score
    # --------------------------------------------------------

    df["fund_score"] = (

        0.30 * df["return_score"]

        + 0.25 * df["sharpe_score"]

        + 0.20 * df["alpha_score"]

        + 0.15 * df["expense_score"]

        + 0.10 * df["drawdown_score"]
    )

    # Convert score to 0-100
    df["fund_score"] = df["fund_score"] * 100

    return df


# ============================================================
# 6. RISK PROFILE FILTER
# ============================================================

def filter_by_risk(df, risk_profile):

    risk_profile = risk_profile.lower()

    if risk_profile == "low":

        # Conservative investors
        filtered = df[
            df["risk_category"]
            .astype(str)
            .str.lower()
            .isin([
                "low",
                "low risk",
                "moderately low"
            ])
        ]

    elif risk_profile == "moderate":

        filtered = df[
            df["risk_category"]
            .astype(str)
            .str.lower()
            .isin([
                "moderate",
                "moderately high"
            ])
        ]

    elif risk_profile == "high":

        filtered = df[
            df["risk_category"]
            .astype(str)
            .str.lower()
            .isin([
                "high",
                "very high"
            ])
        ]

    else:

        return pd.DataFrame()

    return filtered


# ============================================================
# 7. RECOMMEND FUNDS
# ============================================================

def recommend_funds(df, risk_profile, top_n=5):

    filtered_df = filter_by_risk(
        df,
        risk_profile
    )

    if filtered_df.empty:

        return filtered_df

    # Sort according to fund score
    recommendations = filtered_df.sort_values(
        by="fund_score",
        ascending=False
    )

    recommendations = recommendations.head(top_n)

    return recommendations


# ============================================================
# 8. DISPLAY RESULTS
# ============================================================

def display_recommendations(recommendations):

    if recommendations.empty:
        return

    columns_to_show = [
        "scheme_name",
        "category",
        "risk_category",
        "return_3yr_pct",
        "sharpe_ratio",
        "alpha",
        "expense_ratio_pct_performance",
        "max_drawdown_pct",
        "fund_score"
    ]

    # Show only columns which actually exist
    available_columns = [
        col
        for col in columns_to_show
        if col in recommendations.columns
    ]

    result = recommendations[available_columns].copy()

    


# ============================================================
# 9. SAVE RECOMMENDATIONS
# ============================================================

def save_recommendations(
    recommendations,
    risk_profile
):

    output_directory = "content"

    os.makedirs(
        output_directory,
        exist_ok=True
    )

    output_file = (
        f"{output_directory}/"
        f"recommendations_{risk_profile}.csv"
    )

    recommendations.to_csv(
        output_file,
        index=False
    )

    


# ============================================================
# 10. MAIN PROGRAM
# ============================================================

def main():

    # Load data
    fund_master, performance = load_data()

    # Prepare data
    df = prepare_data(
        fund_master,
        performance
    )

    # Calculate score
    df = calculate_score(df)

    
    choice = input(
        "\nEnter your choice (1/2/3): "
    )

    if choice == "1":

        risk_profile = "low"

    elif choice == "2":

        risk_profile = "moderate"

    elif choice == "3":

        risk_profile = "high"

    else:

        

        return

    # Generate recommendations
    recommendations = recommend_funds(
        df,
        risk_profile,
        top_n=5
    )

    # Display results
    display_recommendations(
        recommendations
    )

    # Save results
    save_recommendations(
        recommendations,
        risk_profile
    )


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()