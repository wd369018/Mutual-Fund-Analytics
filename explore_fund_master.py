import pandas as pd

df = pd.read_csv('data/raw/01_fund_master.csv')

print('=== Fund Master Exploration ===')
print()
print('Unique Fund Houses:')
for house in sorted(df['fund_house'].unique()):
    print(f'  - {house}')
print()

print('Unique Categories:')
for cat in sorted(df['category'].unique()):
    print(f'  - {cat}')
print()

print('Unique Sub-Categories:')
for sub in sorted(df['sub_category'].unique()):
    print(f'  - {sub}')
print()

print('Unique Risk Categories:')
for risk in sorted(df['risk_category'].unique()):
    print(f'  - {risk}')
print()

print('AMFI Code Structure:')
print(f'  Min code: {df["amfi_code"].min()}')
print(f'  Max code: {df["amfi_code"].max()}')
print(f'  Total unique codes: {df["amfi_code"].nunique()}')
print(f'  Code range sample: {list(df["amfi_code"].unique()[:5])}...')