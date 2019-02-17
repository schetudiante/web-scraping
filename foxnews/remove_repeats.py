"""
Removes repeats from ./fox_data/fox.csv and writes
result to ./fox_data/fox2.csv
"""
import csv
import sys
import json

seen = set()
with open('./fox_data/fox.csv', 'rt') as f:
    reader = csv.DictReader(f)
    with open('./fox_data/fox2.csv', 'wt') as f:
        writer = csv.DictWriter(f, reader.fieldnames)
        writer.writeheader()
        for row in reader:
            name_date = (row['title'], row['date'][:10], row['domain'])
            if name_date in seen:
                print('Skipping repeat {}'.format(name_date))
                continue
            if row['author'] and not row['author'][0].isupper():
                row['author'] = ''
            row['links'] = json.dumps(row['links'])
            sys.stdout.write('\r{}'.format(row['date']))
            seen.add(name_date)
            writer.writerow(row)
