import sqlite3
from pathlib import Path

conn = sqlite3.connect(Path('C:/Users/wd369/OneDrive/Desktop/myrepo/Mutual-Fund-Analytics/database/bluestock_mf.db'))
print('dim_fund fund_house values (first 10):')
for row in conn.execute('SELECT fund_house FROM dim_fund LIMIT 10'):
    print(f'  "{row[0]}"')
print('\nTotal rows:', conn.execute('SELECT COUNT(*) FROM dim_fund').fetchone()[0])
conn.close()