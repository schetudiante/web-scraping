import requests
import re
import traceback
import sys
from bs4 import BeautifulSoup as bsoup
from pathos.multiprocessing import ProcessPool as Pool

NUM_PROC = 32

urls_path = './output/urls.txt'
completed_urls_path = './output/completed_urls.txt'
problem_urls_path = './output/problem_urls.txt'

with open(urls_path, 'rt') as f:
    URLS = set(f.read().split())

with open(completed_urls_path, 'rt') as f:
    COMPLETED_URLS = set(f.read().split())

with open(problem_urls_path, 'rt') as f:
    PROBLEM_URLS = set(f.read().split())

req_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def condense_text(article_element):
    text = ' '.join(article_element.findAll(text=True))
    text = ' '.join(text.split())
    return text

def add_problem_url(url):
    with open(problem_urls_path, 'a') as f:
        f.write('{}\n'.format(url))

def add_completed_url(url):
    with open(completed_urls_path, 'a') as f:
        f.write('{}\n'.format(url))

def get_fname(url):
    url = url.replace('https:', 'http:')
    url = url.replace('http://foxnews.com', '')
    url = url.strip().strip('/')
    url = url.replace('.html', '')
    url = url.replace('/', '_')
    url = url.replace('%', '')
    url = url.replace('\'', '-')
    return './output/articles/{}'.format(url)[:128]

def get_content(url):
    try:
        html = requests.get(url, headers=req_headers).text
        soup = bsoup(html, 'html5lib')
        article_text = soup.find(class_='article-text')
        article_body = soup.find(class_='article-body')

        content_element = article_text or article_body
        if content_element:
            with open(get_fname(url), 'wt') as f:
                f.write(condense_text(content_element))
            add_completed_url(url)
            return True
    except:
        print('Problem while parsing: {}'.format(url))
        traceback.print_exc()
    add_problem_url(url)
    return False


if __name__ == '__main__':
    total_url_count = len(URLS)
    completed_urls_count = len(COMPLETED_URLS)
    problem_urls_count = len(PROBLEM_URLS)
    preprocessed_count = completed_urls_count + problem_urls_count
    unprocessed_urls = sorted((URLS - COMPLETED_URLS) - PROBLEM_URLS)
    pool = Pool(nodes=NUM_PROC)
    results = pool.uimap(get_content, unprocessed_urls)
    for i, success in enumerate(results):
        i += preprocessed_count
        sys.stderr.write('\rdone {0:%} ({1:d}/{2:d}) bad:{3}'.format(
        i/total_url_count, i, total_url_count, problem_urls_count))
        sys.stderr.flush()

        if success:
            completed_urls_count += 1
        else:
            problem_urls_count += 1
