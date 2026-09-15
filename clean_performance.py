import pandas as pd
from pathlib import Path

BASE = Path('C:/Users/wd369/OneDrive/Desktop/myrepo/Mutual-Fund-Analytics')
RAW = BASE / 'data' / 'raw'
PROCESSED = BASE / 'data' / 'processed'

# Load raw scheme performance data
perf = pd.read_csv(RAW / '07_scheme_performance.csv')

print(f'Raw performance shape: {perf.shape}')
print(f'Columns: {list(perf.columns)}')

# 1. Validate all return values are numeric
numeric_columns = [
    'return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct',
    'benchmark_3yr_pct', 'alpha', 'beta',
    'sharpe_ratio', 'sortino_ratio', 'std_dev_ann_pct', 'max_drawdown_pct'
]

for column in numeric_columns:
    if column in perf.columns:
        perf[column] = pd.to_numeric(perf[column], errors='coerce')
        # Flag NaN values (originally non-numeric)
        nan_count = perf[column].isna().sum()
        if nan_count > 0:
            print(f'  ⚠ {column}: {nan_count} non-numeric values coerced to NaN')

# 2. Check expense_ratio range (0.1% – 2.5%)
if 'expense_ratio_pct' in perf.columns:
    print(f'\nExpense ratio range: {perf["expense_ratio_pct"].min():.2f}% - {perf["expense_ratio_pct"].max():.2f}%')
    min_exp = 0.1
    max_exp = 2.5
    anomalous_expense = perf[(perf['expense_ratio_pct'] < min_exp) | (perf['expense_ratio_pct'] > max_exp)]
    print(f'Anomalous expense ratios (< {min_exp}% or > {max_exp}%): {len(anomalous_expense)}')
    if len(anomalous_expense) > 0:
        print(f'  Examples:')
        for _, row in anomalous_expense.head(3).iterrows():
            print(f'    - {row["scheme_name"]}: {row["expense_ratio_pct"]}%')

# 3. Check for any other anomalies
print(f'\nSummary of checks:')
print(f'  - amfi_code non-null: {perf["amfi_code"].notna().sum()}/{len(perf)}')
print(f'  - return_5yr_pct range: {perf["return_5yr_pct"].min():.2f}% - {perf["return_5yr_pct"].max():.2f}%')
print(f'  - sharpe_ratio range: {perf["sharpe_ratio"].min():.2f} - {perf["sharpe_ratio"].max():.2f}')
print(f'  - max_drawdown_pct range: {perf["max_drawdown_pct"].min():.2f}% - {perf["max_drawdown_pct"].max():.2f}%')

# 3. Check risk_grade consistency with risk_category
print(f'\nRisk grade distribution: {perf["risk_grade"].value_counts().to_dict()}')
print(f'Risk grade distribution: {perf["risk_grade"].value_counts().to_dict()}')

# 4. Reset index
perf = perf.reset_index(drop=True)

# Save cleaned data
output_path = PROCESSED / 'Cleaned_07_scheme_performance.csv'
perf.to_csv(output_path, index=False)

print(f'\nCleaned performance shape: {perf.shape}')
print(f'Saved to: {output_path}')