import csv
import os

csv_dir = './output/csv/'
csv_paths = os.listdir(csv_dir)
urls = set()

for path in csv_paths:
    with open(csv_dir + path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            urls.add(row['url'])

with open('output/urls.txt', 'wt') as f:
    for url in sorted(urls):
        f.write('{}\n'.format(url))
