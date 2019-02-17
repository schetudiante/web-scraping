import os
import requests
import traceback
import sys
import csv
import json
import time
from random import random
from bs4 import BeautifulSoup as bsoup
from pathos.multiprocessing import ProcessPool as Pool

NUM_PROC = 12
base_forum_url = 'https://www.stormfront.org/forum/{forum_id}-{page_num}'
forum_data_path = './output/forums.csv'
forum_pages_path = './output/forum_pages/{}.html'

with open(forum_data_path, 'rt') as f:
    forum_data = list(csv.DictReader(f))

def get_forum_id(forum_url):
    return forum_url.split('/')[-2]

def get_total_pages(forum_soup):
    tds = forum_soup.findAll('td', class_='vbmenu_control')
    for td in tds:
        if td.text.startswith('Page'):
            return int(td.text.split()[-1])
    return 1

def save_html(url):
    fpath = forum_pages_path.format(url.replace('https://www.', '').replace('/', '_'))
    if os.path.exists(fpath):
        print('Skipping {}, already saved.'.format(url))
        return
    try:
        time.sleep(random() * 2)
        text = requests.get(url).text
        with open(fpath, 'wt') as f:
            f.write(text)
        print('Saved {}'.format(url))
    except:
        traceback.print_exc()
        print('Problem when trying to save:', url)

if __name__ == '__main__':
    pool = Pool(nodes = NUM_PROC)
    for row in forum_data:
        url, title, categories = row['url'], row['title'], row['categories']
        soup = bsoup(requests.get(url).text, features = 'html5')
        print('Total pages for {}: {}'.format(url, get_total_pages(soup)))
        total_pages = get_total_pages(soup)
        forum_id = get_forum_id(url)
        urls = [base_forum_url.format(forum_id=forum_id, page_num=page_num) for page_num in range(1, total_pages + 1)]
        results = pool.uimap(save_html, urls)
        list(results)
        del soup
