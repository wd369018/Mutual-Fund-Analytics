import requests
import pandas as pd
from pathlib import Path

# Fetch live NAV for HDFC Top 100 Direct (125497)
url = 'https://api.mfapi.in/mf/125497'
response = requests.get(url)
data = response.json()

print('Live NAV API Response:')
print('Status: OK')
print(f'Number of NAV records: {len(data["data"])}')

# Parse and save as CSV
nav_data = data['data']
df = pd.DataFrame(nav_data)
print(f'\nDataFrame shape: {df.shape}')
print(f'Columns: {list(df.columns)}')
print(f'Head:')
print(df.head())

# Save to raw directory
output_path = Path('C:/Users/wd369/OneDrive/Desktop/myrepo/Mutual-Fund-Analytics/data/raw/live_nav_api.csv')
df.to_csv(output_path, index=False)
print(f'\nSaved to: {output_path}')