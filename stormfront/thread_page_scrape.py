import requests
import csv
import os
import traceback
import time
import random
from bs4 import BeautifulSoup as bsoup
from pathos.multiprocessing import ProcessPool as Pool

output_dir = './output/thread_pages/'
input_file = './output/thread_urls.csv'
NUM_PROC = 8

def clean_url(url):
    if '?' in url:
        url = url[:url.index('?')]
    url = url[:-1]
    return url

def scrape_thread(url):
    url = clean_url(url)
    try:
        thread_dir = output_dir + url.replace('https://www.', '').replace('/', '_') +'/'
        os.mkdir(thread_dir)
        print('Created directory:', thread_dir)
    except OSError:
        print('Directory for {} already exists, skipping'.format(url))
        return
    try:
        print('Requesting {}'.format(url))
        text = requests.get(url).text
        soup = bsoup(text, features='html5lib')
        num_pages = get_number_pages(soup)
        with open(thread_dir + 'num_pages.txt', 'wt') as f:
            f.write(str(num_pages))
        for p in range(1, num_pages + 1):
            rest()
            if p > 1:
                page_url = url + '-' + str(p)
                print('Requesting:', page_url)
                text = requests.get(page_url).text
            page_path = thread_dir + str(p) + '.html'
            print('Writing to', page_path)
            with open(page_path, 'wt') as f:
                f.write(text)
        return url, num_pages
    except KeyboardInterrupt:
        print('Exiting')
        raise KeyboardInterrupt
    except:
        traceback.print_exc()

def get_number_pages(soup):
    tds = soup.findAll('td', class_='vbmenu_control')
    for td in tds:
        text = td.text.strip()
        if text.startswith('Page'):
            tokens = text.split()
            return int(tokens[-1])
    return 1

def rest():
    time.sleep(random.random() * 2)


if __name__ == '__main__':
    pool = Pool(nodes = NUM_PROC)
    with open(input_file) as f:
        links = (row['link'] for row in csv.DictReader(f))
        results = pool.uimap(scrape_thread, links)
        for r in results:
            print(r)
            rest()

