"""
Iterates through URLs in ./api_data and populates
./articles with articles
"""
import requests
import re
import traceback
import sys
import csv
import json
import os
from bs4 import BeautifulSoup as bsoup
from pathos.multiprocessing import ProcessPool as Pool

NUM_PROC = 16 # 32 might be fine, but I get blocked

META_DIR = os.path.join('.', 'meta')
if not os.path.exists(META_DIR):
    os.mkdir(META_DIR)

CSV_PATH = os.path.join(META_DIR, 'articles.csv')
if not os.path.exists(CSV_PATH):
    raise Exception('articles.csv not found')

sys.stdout.write('\rLoading articles...')
with open('articles.csv', 'rt') as f:
    reader = csv.DictReader(f)
    URLS = {row['url'] for row in reader if row['category'] is not 'video' and 'video' not in row['domain']}
    sys.stdout.write('Articles loaded!\n')

completed_urls_path = os.path.join('.', 'meta', 'completed.txt')
with open(completed_urls_path, 'rt') as f:
    COMPLETED_URLS = set(f.read().split())

problem_urls_path   = os.path.join('.', 'meta', 'problem.txt')
with open(problem_urls_path, 'rt') as f:
    PROBLEM_URLS = set(f.read().split())

req_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def condense_text(article_element):
    text = '\n'.join([ae.strip() for ae in article_element.findAll(text=True) if ae.strip()])
    text.replace('Continue Reading Below', '')
    text.replace('Continue reading below', '')
    return text

def add_problem_url(url):
    with open(problem_urls_path, 'a') as f:
        f.write('{}\n'.format(url))

def add_completed_url(url):
    with open(completed_urls_path, 'a') as f:
        f.write('{}\n'.format(url))

def get_fname(url):
    url = url.replace('https:', 'http:')
    url = url.strip().strip('/')
    url = url.replace('.html', '')
    url = url.replace('/', '_')
    url = url.replace('%', '')
    url = url.replace('\'', '-')
    return './articles/{}.json'.format(url)[:128]

def get_source(url, soup):
    source, author = None, None
    if 'foxbusiness.com' in url:
        source = soup.find('span', class_='source')
        source = source and source.getText()
        author = soup.find('span', class_='author')
        author = author and author.getText()
    elif 'foxnews.com' in url:
        source = soup.find('span', class_='article-source')
        source = source and source.getText()
        author = soup.find(class_='author-byline')
        author = author and author.find('a')
        if author and author['href'].startswith('/person/'):
            author = author.getText()
        else:
            author = None
    if source:
        source = source.strip('| ')
    if author:
        author = author.strip('| ')
    return source, author

def get_content(url):
    try:
        request = requests.get(url, headers=req_headers, allow_redirects=True)
        html = request.text
        redirect_url = request.url
        soup = bsoup(html, features='lxml')
        source, author = get_source(url, soup)
        article_text = soup.find(class_='article-text')
        article_body = soup.find(class_='article-body')
        article_content = soup.find(class_='article-content')
        
        content_element = article_text or article_body or article_content
        if content_element:
            urls = [link['href'] for link in content_element.findAll('a') if 'href' in link.attrs]
            with open(get_fname(url), 'wt') as f:
                text = condense_text(content_element)
                data = {'author': author or '', 'redirect':redirect_url, 'source': source or '', 'text': text, 'links': urls}
                json.dump(data, f, indent = 4, sort_keys=True)
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
    unprocessed_urls = (URLS - COMPLETED_URLS) - PROBLEM_URLS
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
