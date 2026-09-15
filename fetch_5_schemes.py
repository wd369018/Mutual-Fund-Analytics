import requests
import pandas as pd

# NAV codes for 5 key schemes
scheme_codes = {
    'SBI Bluechip': 119551,
    'ICICI Bluechip': 120503,
    'Nippon Large Cap': 118632,
    'Axis Bluechip': 119092,
    'Kotak Bluechip': 120841
}

for name, code in scheme_codes.items():
    url = f'https://api.mfapi.in/mf/{code}'
    response = requests.get(url)
    data = response.json()
    nav_data = data['data']
    df = pd.DataFrame(nav_data)
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df['nav'] = pd.to_numeric(df['nav'])
    print(f'{name} (Code: {code}): {len(df)} records')
    print(f'  Date range: {df["date"].min().strftime("%Y-%m-%d")} to {df["date"].max().strftime("%Y-%m-%d")}')
    print(f'  NAV range: {df["nav"].min():.2f} to {df["nav"].max():.2f}')
    print()