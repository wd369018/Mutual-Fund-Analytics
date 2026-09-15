import pandas as pd

df = pd.read_csv('data/raw/08_investor_transactions.csv')
print('Original transaction_type values (first 30):')
print(df['transaction_type'].value_counts().head(30))
print()
print('Sample values:')
for i, val in enumerate(df['transaction_type'].unique()[:20]):
    print(f'  "{val}"')