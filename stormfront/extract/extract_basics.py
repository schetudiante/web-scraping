from models import *
import csv

odir = './data/'

fheader = ['forum_id', 'url', 'title', 'categories']
with open(odir + 'forums.csv', 'wt') as f:
    writer = csv.DictWriter(f, fheader)
    writer.writeheader()
    for f in Forum.select().order_by(Forum.id):
        row = {
            'forum_id':f.id,
            'url':f.url,
            'title':f.title,
            'categories':f.categories
        }
        writer.writerow(row)

theader = ['thread_id', 'forum_id', 'url', 'title', 'timestamp']
with open(odir + 'threads.csv', 'wt') as f:
    writer = csv.DictWriter(f, theader)
    writer.writeheader()
    for t in Thread.select().order_by(Thread.id):
        row = {
            'thread_id':t.id,
            'forum_id':t.forum,
            'title':t.title,
            'url':t.url,
            'timestamp':t.timestamp
        }
        writer.writerow(row)
