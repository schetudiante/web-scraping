import csv
import os

base_url = 'http://foxnews.com/'

csv_path = './output/csv/'
csv_fnames = map(lambda fname: csv_path + fname, os.listdir(csv_path))

def get_category(csv_row):
    url = csv_row.get('topic_url', '')
    if url.startswith(base_url):
        return url.replace(base_url, '').replace('.html', '')
    return None

categories_path = './input/categories.txt'
with open(categories_path, 'rt') as f:
    categories = set(f.read().split())

csv_dicts = []
for csv_fname in csv_fnames:
    with open(csv_fname, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            topic_url = get_category(row)
            if topic_url:
                categories.add(topic_url)

with open(categories_path, 'wt') as f:
    for category in categories:
        f.write(category + '\n')
