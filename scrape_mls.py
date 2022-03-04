import threading
from multiprocessing import Process, Lock, Pool, Queue
from queue import Queue
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import time
import re
import datetime as dt
from url_mls_searches import mls_search_urls

class Listing(list):
    def __init__(self):
        self.lock = threading.Lock()
    def append_listing(self,obj):
        self.lock.acquire()
        try:
            self.append(obj)
        finally:
            self.lock.release()

def get_listing_details(url,listings,i):

    listing_start = time.time()

    # Data arguments that need to be included in the url request in order to extract listing specific page/data
    data = {
        '__EVENTTARGET':'_ctl0$m_DisplayCore',
        '__EVENTARGUMENT': f'Redisplay|69,,{i}'
    }

    ### Request specific listing page/data ###
    listing_page = requests.post(url,data=data)
    listing_soup = BeautifulSoup(listing_page.content,'html.parser')
    listing_req_time = time.time()
    print(f"Request = {listing_req_time-listing_start}s")

    ### Parsing / Extracting listing properties ###
    listing_details = {}
    listing_details.setdefault('Address',listing_soup.find_all('span',class_='formula J_formula')[0].text)
    listing_details.setdefault('City',listing_soup.find_all('span',class_='formula J_formula')[1].text.split(',')[0].lstrip())
    listing_details.setdefault('Province',listing_soup.find_all('span',class_='formula J_formula')[1].text.split(' ')[2])
    listing_details.setdefault('Postal Code','-'.join(listing_soup.find_all('span',class_='formula J_formula')[1].text.split(' ')[-2:]))
    listing_details.setdefault('Listing Status',listing_soup.find_all('span',class_='formula J_formula')[3].text)
    listing_details.setdefault('Listing Agency',re.sub('Courtesy of ','',listing_soup.find_all('span',class_='formula J_formula')[-1].text))
    for j in range(len(listing_soup.find_all('span',class_='formula')[4].find_all('span','d-text'))):
        listing_details.setdefault(listing_soup.find_all('span',class_='formula')[4].find_all('span','d-textStrong')[j].text,listing_soup.find_all('span',class_='formula')[4].find_all('span','d-text')[j].text)
    listing_details.setdefault('Timestamp',dt.date.today())

    listings.append_listing(listing_details)
    listing_end = time.time()

    print(f'Dictionary list = {listing_end-listing_req_time}s')
    print(f'Thread {i} = {listing_end-listing_start}s')
    return listing_details

def main_multithread():

    print(f'Started {dt.datetime.now()}')
    script_start = time.time()

    #######################
    ### Retrieving data ###
    #######################

    ### Setup config ###
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
    url = 'https://matrix.pillarnine.com/Matrix/Public/Portal.aspx?L=1&k=4077049XXbcJ&p=CS-1999394-0#1' # <$500k Downtown Calgary Colin
    # url = 'https://matrix.pillarnine.com/Matrix/Public/Portal.aspx?ID=0-309658072-10&eml=a2oua3dhbjg4QGdtYWlsLmNvbQ==#1' # <$425k SW/NW Calgary Condos & Townhouses Elizabeth
    # urls = {'<$500k Downtown': 'https://matrix.pillarnine.com/Matrix/Public/Portal.aspx?L=1&k=4077049XXbcJ&p=CS-1999394-0#1',
    #         '<$425k SW/NW Condos':'https://matrix.pillarnine.com/Matrix/Public/Portal.aspx?ID=0-309658072-10&eml=a2oua3dhbjg4QGdtYWlsLmNvbQ==#1'}

    page = requests.get(url,headers=headers)
    req_end = time.time()
    print(f'Request = {req_end-script_start}s')

    ####################
    ### Parsing data ###
    ####################

    soup = BeautifulSoup(page.content,'html.parser')
    total_listings = int(soup.find('b').text) # Need to determine the number of listings that need to be parsed
    print(f"Total Listings = {total_listings}")
    parse_end = time.time()
    print(f'Parse = {parse_end-req_end}s')

    ###########################################################
    ### Parsing & Extracting Listings Data (Multi-threaded) ###
    ###########################################################

    listings = Listing()
    threads = []

    for i in range(total_listings):
        t = threading.Thread(target=get_listing_details, args=(url,listings,i,))
        t.start()
        threads.append(t)
    threads_end = time.time()
    print(f'Thread end = {threads_end-parse_end}s')

    counter = 0
    for thread in threads:
        join_start = time.time()
        print(f'Joining thread {counter}')
        thread.join()
        join_end = time.time()
        print(f'Joined thread {counter}. Time = {join_end-join_start}s')
        counter += 1

    threads_join_end = time.time()
    print(f'Threads Join End = {threads_join_end-threads_end}s')

    #############################
    ### Saving & Storing Data ###
    #############################

    df = pd.DataFrame(listings)
    today = dt.date.today()

    df.to_csv(f'./data/{today.year}-{today.month if today.month>9 else "0"+str(today.month)}-{today.day if today.day>9 else "0"+str(today.day)} - lt500k Downtown - mls (raw).csv',index_label=False)
    df.to_csv(f'./data/{today.year}-{today.month if today.month>9 else "0"+str(today.month)}-{today.day if today.day>9 else "0"+str(today.day)} - mls (raw).csv',index_label=False)
    # df.to_csv(f'./data/{today.year}-{today.month if today.month>9 else "0"+str(today.month)}-{today.day if today.day>9 else "0"+str(today.day)} - mls - Elizabeth (raw).csv')

    script_end = time.time()
    print(f'Total run = {script_end-script_start}s')

def get_mls_search_data(title,url):

    print(f'Started {dt.datetime.now()}')
    script_start = time.time()

    #######################
    ### Retrieving data ###
    #######################

    ### Setup configs ###
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}

    page = requests.get(url,headers=headers)
    req_end = time.time()
    print(f'Request = {req_end-script_start}s')

    ####################
    ### Parsing data ###
    ####################

    soup = BeautifulSoup(page.content,'html.parser')
    total_listings = int(soup.find('b').text) # Need to determine the number of listings that need to be parsed
    print(f"Total Listings = {total_listings}")
    parse_end = time.time()
    print(f'Parse = {parse_end-req_end}s')

    ###################################################
    ### Parsing & Extracting Listings Specific Data ###
    ###################################################

    listings = Listing()

    for i in range(total_listings):
        get_listing_details(url,listings,i)

    #############################
    ### Saving & Storing Data ###
    #############################

    df = pd.DataFrame(listings)
    today = dt.date.today()

    df.to_csv(f'./data/{today.year}-{today.month if today.month>9 else "0"+str(today.month)}-{today.day if today.day>9 else "0"+str(today.day)} - {title} - mls (raw).csv',index_label=False)
    print(f'Saved {today.year}-{today.month if today.month>9 else "0"+str(today.month)}-{today.day if today.day>9 else "0"+str(today.day)} - {title} - mls (raw).csv')

    script_end = time.time()
    print(f'Total run = {script_end-script_start}s')

def main():
    for mls_search in mls_search_urls:
        get_mls_search_data(mls_search['title'],mls_search['url'])

def main_mp():

    processes = []

    for mls_search in mls_search_urls:
        p = Process(target=get_mls_search_data, args=(mls_search['title'],mls_search['url'],))
        processes.append(p)
        p.start()

    for process in processes:
        process.join()

if __name__ == '__main__':
    # main_multithread()
    main()
