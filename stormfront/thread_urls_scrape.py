import requests
import os
import csv
from bs4 import BeautifulSoup as bsoup

forum_page_dir = './output/forum_pages/'
forum_page_files = (forum_page_dir + fname for fname in os.listdir(forum_page_dir))
output_path = './output/thread_urls.csv'
csv_headers = ['title', 'forum_id', 'link']

with open(output_path, 'wt') as f:
    writer = csv.DictWriter(f, csv_headers)
    writer.writeheader()

def get_forum_id(fname):
    fname = fname.replace('./output/forum_pages/stormfront.org_forum_', '')
    fname = fname.replace('.html', '')
    if fname.index('-') > 0:
        fname = fname[:fname.index('-')]
    return fname


def csv_write(rows):
    with open(output_path, 'at') as f:
        writer = csv.DictWriter(f, csv_headers)
        for row in rows:
            writer.writerow(row)

for fname in forum_page_files:
    print(fname)
    fid = get_forum_id(fname)
    with open(fname, 'rt') as f:
        soup = bsoup(f.read(), features='html5lib')
    rows = []
    for a in soup.findAll('a', href=True):
        row = {'forum_id': fid}
        tag_id = a.get('id')
        if tag_id and tag_id.startswith('thread_title_'):
            print(a.get('href'), a.get('id')) 
            row['title'] = a.text.strip()
            row['link'] = a.get('href')
            rows.append(row)
    csv_write(rows)

