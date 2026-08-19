"""
Live NAV fetching module.

This script fetches latest mutual-fund NAV data and saves it
to the processed data directory.
"""


import pandas as pd
import requests
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(PROCESSED_PATH, exist_ok=True)


url = "https://api.mfapi.in/mf/125497"

response = requests.get(url)

data = response.json()


nav_data = data["data"]


df = pd.DataFrame(nav_data)





df.to_csv(
    os.path.join(PROCESSED_PATH, "live_nav.csv"),
    index=False
)

