from models import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
import csv
import os

if not os.path.exists('./data'):
    os.mkdir('./data')

if not os.path.exists('./data/full_by_date'):
    os.mkdir('./data/full_by_date/')

out_path = './data/full_by_date/'
start_date = datetime(2001, 8, 1)
end_date = datetime(2019,1,1)
increment = relativedelta(months=1)
csv_headers = ['comment_id', 'thread_id', 'thread_position', 'author', 'timestamp', 'content', 'links']

while start_date < end_date:
    year_dir = out_path + str(start_date.year) + '/'
    month_path = year_dir + str(start_date.month) + '.csv'
    if not os.path.exists(year_dir):
        os.mkdir(year_dir)
    comments = Comment.select().where(\
        (Comment.timestamp >= start_date) &
        (Comment.timestamp < start_date + increment)).order_by(Comment.timestamp)
    print('start:', start_date)
    total=0
    with open(month_path, 'wt') as f:
        writer = csv.DictWriter(f,csv_headers)
        writer.writeheader()
        for c in comments:
            total += 1
            row = {\
                'comment_id':c.id,
                'thread_id':c.thread,
                'thread_position':c.comment_num,
                'author': c.author,
                'timestamp':c.timestamp,
                'content':c.content,
                'links':c.links
            }
            writer.writerow(row)
    print('found', total, 'comments')
    start_date += increment
