"""
Scrapes article URLs and metadata from Fox's (exposed :])
content API (normally used for search requests). Will
occasionally invoke some kind of error on their backend,
but otherwise pretty consistent.

Writes the data it finds to ./api_data
"""
import json
import time
import requests
import traceback
import sys
import os
from pathos.multiprocessing import ProcessPool as Pool

"""
Alternate API link, seems to fail for approximately offset > 97000:
https://www.foxnews.com/api/article-search?isCategory=true&
isTag=false&isKeyword=false&isFixed=false&isFeedUrl=false&
searchSelected=politics&contentTypes=%7B%22interactive%22
:true,%22slideshow%22:true,%22video%22:true,%22article%22:true%
7D&size=11&offset=21
"""

# Base API url with formatting slot for start index
API_BASE = (
    'https://api.foxnews.com/v1/content/search?'
    'q=the&' # We actually just search for every article containing "the"
    'fields=date,description,title,url,type,taxonomy&'
    'start={start}&'
    'sort=latest'
)

MAX_ATTEMPTS = 150 # Max attempts before giving up on an index
NUM_PROC = 8 # Number of processes desired
             # Raising this past 8 actually DOS's Fox's API lol
             # Basically, just keep it at 8.
OUTPUT_DIR = os.path.join('.', 'api_data') # The directory. For output.
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

#Set of ints corresponding to positions in API scraped
completed = set(map(
    lambda s: int(s[:-5]), #Shaves off ".json" and converts to int
    os.listdir(OUTPUT_DIR)
))

"""
Checks the API and pulls out current number of articles.
Returns int of the number of articles.
"""
def get_num_articles():
    # Try 50 times before giving up
    for i in range(50):
        try:
            sys.stdout.write(
                '\rGetting number of articles' + '.' * (i % 3 + 1)
            ) # module term is purely stylistic decision
            sys.stdout.flush()

            # Grab first page of API and extract numFound value
            data = requests.get(API_BASE.format(start=0)) 
            num_found = int(data.json()['response']['numFound'])
            sys.stdout.write('\rRetrieved number of articles: {}\n'.format(num_found))
            return num_found
        except:
            # Error catch all. Probably bad practice \-(x_x)-\
            traceback.print_exc()
            time.sleep(1) # Back off for a second before retrying

    # If you're down here, then the API is probably down too
    raise Exception('Repeated problems while attempting to get number of pages. '
                    'The API may be down.')

# I hate to be the kind of person that sets a global variable
# its a lot messier without using this.
num_articles = get_num_articles()

"""
Takes in the tuple (index, num_articles)
If successful, saves a json corresponding to the
index of the articles retrieved.

Returns string representing success status and
number of articles.

Note: The reason num_articles is both passed
in and out is because the number of articles
can change during the course of execution.
"""
def scrape_index(args):
    index, num_articles = args
    for i in range(MAX_ATTEMPTS):
        try:
            # Calculate start from index
            start = num_articles - index
            data = requests.get(API_BASE.format(start=start))
            if data.text.startswith('Internal'):
                return 'ISError', index, num_articles

            # check numFound
            data = data.json()['response']
            num_found = int(data['numFound'])

            if num_found != num_articles:
                # num_articles changed during course of execution
                # start index must be recomputed and a re-requested
                num_articles = num_found
                continue

            opath = os.path.join(OUTPUT_DIR, '{}.json'.format(index))
            with open(opath, 'wt') as f:
                json.dump(data['docs'], f, indent=4)
                return 'Success', index, num_articles
        except:
            # print('Retrying {}'.format(start))
            time.sleep(.2)
    return 'Reached max attempts', index, num_articles

"""
Generator function that yields the lowest unvisited
index and the current number of articles
"""
def api_range():
    index = 10
    while index + 10 <= num_articles:
        if index not in completed:
            yield index, num_articles
            time.sleep(.5)
        index += 10

"""
Generates a list of URLs
"""
def generate_url_list():
    files = [
        os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR)
    ]
    urls = set()
    for fpath in files:
        with open(fpath, 'rt') as f:
            try:
                j = json.loads(f.read())
                for a in j:
                    urls.union(a['url'])
            except:
                traceback.print_exc()

if __name__ == '__main__':
    pool = Pool(nodes = NUM_PROC)
    results = pool.uimap(
        scrape_index,   # Function to be mapped onto the api_range func
        api_range(), # Generator for unvisited article indexes in API
        chunksize = NUM_PROC/32
    )
    num_completed = len(completed) * 10
    for result, index, num_articles in results:
        num_completed += 10
        sys.stdout.write(
            '\r{}, {}/{} ({:.3f}%)'
                .format(
                    result, 
                    index, 
                    num_articles, 
                    100.0*num_completed/num_articles
                )
        )
    generate_url_list()
