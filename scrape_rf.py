import pandas as pd
import numpy as np
import os
import time
from bs4 import BeautifulSoup
import requests
import re
import json
import datetime as dt
import seaborn as sns

try:
    # Python 3.x
    from urllib.request import urlopen, urlretrieve, quote
    from urllib.parse import urljoin
except ImportError:
    # Python 2.x
    from urllib import urlopen, urlretrieve, quote
    from urlparse import urljoin

def main():
    listings = []
    for price in range(500,5001,25):
        loop_start = time.time()
        json_url = f'https://www.rentfaster.ca/api/map.json?e=undefined&beds=&baths=&type=&price_range_adv%5Bfrom%5D={price}&price_range_adv%5Bto%5D={price+24}&area=51.18725531061486%2C-113.72722341074217%2C50.90397819717543%2C-114.3877763892578'
        response = urlopen(json_url)
        data = json.loads(response.read().decode("utf-8"))
        listings.extend(data['listings'])
        loop_end = time.time()
        print(f'Completed ${price}-${price+24}. Loop time = {loop_end-loop_start}s')
    df = pd.DataFrame(listings)
    print(f'Total rows = {len(df)}')

    today = dt.datetime.today()
    df['timestamp'] = today
    df.to_csv(f'./data/{today.year}-{today.month if today.month>9 else "0"+str(today.month)}-{today.day if today.day>9 else "0"+str(today.day)} - rf (raw).csv')
    print(f'csv successfully saved.')

if __name__ == '__main__':
    script_start = time.time()
    main()
    script_end = time.time()
    print(f'Total time = {script_end-script_start}s')
