import requests
import csv
import sys
import os
from bs4 import BeautifulSoup as bsoup

s = requests.session()
s.keep_alive = False
request_header = {'Connection':'close'}
NUM_PROC = 8 #Upper limit to prevent getting ratelimit
base_forum_url = 'https://www.stormfront.org/forum/f{}/'
output_path = './output/forums.csv'
csv_headers = ['url', 'title', 'categories']
    
if os.path.isfile(output_path):
    print('Found existing output file. Removing.')
    os.remove(output_path)

with open(output_path, 'wt') as f:
    writer = csv.DictWriter(f, csv_headers)
    writer.writeheader()

def write_csv(row):
    print('Saving:', row)
    with open(output_path, 'at') as f:
        writer = csv.DictWriter(f, csv_headers)
        writer.writerow(row)

def scrape_forums():
    for i in range(10000):
        scrape_num(i)

def scrape_num(i):
    curr_url = base_forum_url.format(i)
    soup = bsoup(requests.get(curr_url, headers = request_header).text, features = 'lxml')
    row = {'url': curr_url}
    row['title'] = soup.title.text
    print(row['title'])
    if ' - Stormfront' in row['title']:
        row['title'] = row['title'].replace(' - Stormfront', '')
    else:
        return
    row['categories'] = 'Stormfront'
    try:
        text = soup.findAll('table', cellspacing=0, cellpadding=0)[1].text
        for c in text.split('\n'):
            if c.startswith('> '):
                row['categories'] += '|{}'.format(c[2:])
    except:
        pass
    write_csv(row)
    del soup



if __name__ == '__main__':
    scrape_forums()
