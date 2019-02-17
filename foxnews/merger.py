import json
import csv
import sys
import re
import traceback

link_re = re.compile('\(\n.+\n\)')

def get_fname(url):
    url = url.replace('https:', 'http:')
    url = url.strip().strip('/')
    url = url.replace('.html', '')
    url = url.replace('/', '_')
    url = url.replace('%', '')
    url = url.replace('\'', '-')
    return './articles/{}.json'.format(url)[:128]

output_file_path = './fox.csv'
input_file_path = 'articles.csv'
headers = ['date', 'title', 'author', 'source', 'description', 'type', 'taxonomy', 'tags', 'domain', 'url', 'redirect', 'category', 'links', 'text']

with open(output_file_path, 'wt') as o:
    writer = csv.DictWriter(o, headers)
    writer.writeheader()
    count = 0
    with open(input_file_path, 'rt') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sys.stdout.write('\r{}'.format(row['date']))
            count += 1
            text_path = get_fname(row['url'])
            try:
                f = open(text_path, 'rt')
                data = json.load(f)
                data['text']= link_re.sub('', data['text'])
                data['links'] = json.dumps(data['links'])
                row.update(data)
                f.close()
            except:
                row['author'] = ''
                row['redirect'] = ''
                row['links'] = json.dumps([])
                row['source'] = ''
                row['text'] = ''
            writer.writerow(row)
