import os

target='Access to this resource on the server'
files = os.listdir('./forum_pages')

for f in sorted(files):
    f = './forum_pages/{}'.format(f)
    delete = False
    with open(f, 'rt') as p:
        if target in p.read():
            delete = True
    if delete:
        print('Removing:', f)
        os.remove(f)
