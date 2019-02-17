#!bin/python3

import sys
import traceback
import datetime
import time
import selenium
from bs4 import BeautifulSoup as bsoup
from selenium import webdriver
import csv

BASE_URL = 'http://foxnews.com{}'
FORMAT_URL = 'http://foxnews.com/{}'
MAX_CLICKS = 5000
HEADER = ['title', 'url', 'topic', 'topic_url']

categories_path = './input/categories.txt'
with open(categories_path, 'rt') as f:
    CATEGORIES = list(filter(lambda c: c, reversed(f.read().split())))

completed_path = './input/completed_categories.txt'
def get_completed():
    with open(completed_path, 'rt') as f:
        return set(f.read().split())

def add_completed(category):
    with open(completed_path, 'a') as f:
        f.write('{}\n'.format(category))

#Sets up webdriver to ignore css and images
def get_driver():
    sys.stdout.write("Setting up webdriver...\r")
    sys.stdout.flush()
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.stylesheet', 2)
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    result = webdriver.Firefox(firefox_profile)
    sys.stdout.write("Finished setting up webdriver.\n")
    return result

#formats base filename
def get_filename(category, curr_time):
    category = category.replace('/', '_')
    return '{0}_{1}_{2:02d}_{3:02d}_{4:02d}_{5:02d}'.format(category, curr_time.year, curr_time.month,
                                                          curr_time.day, curr_time.hour, curr_time.minute)

def click_failsafe(button):
    for _ in range(5):
        try:
            button.click()
            time.sleep(.5)
            return
        except:
            time.sleep(1)
            print("Retrying...")
    raise Exception("Out of attempts.")

def expand_url(url):
    if url.startswith('http'):
        return url
    return BASE_URL.format(url)

def parse_article_preview(preview):
    parsed = dict()
    link = preview.findChild(class_='title').findChild('a')
    topic_span = preview.findChild(class_='eyebrow')
    parsed['title'] = link.text.strip()
    parsed['url'] = expand_url(link['href']).strip()
    if topic_span:
        parsed['topic'] = topic_span.text.strip()
        parsed['topic_url'] = expand_url(topic_span.findChild('a')['href']).strip()
    else:
        parsed['topic'] = ''
        parsed['topic_url'] = ''
    return parsed

def parse_article_previews(articles_previews):
    parsed_previews = []
    bad_previews = 0
    for preview in articles_previews:
        try:
            result = parse_article_preview(preview)
            parsed_previews.append(result)
        except(AttributeError, TypeError) as e:
            bad_previews += 1
    if bad_previews:
        print("{} problems while parsing previews.".format(bad_previews))
    return parsed_previews


for category in CATEGORIES:
    if category in get_completed():
        continue
    add_completed(category)
    print('Starting category: {}'.format(category))
    driver = get_driver()
    curr_time = datetime.datetime.now()
    fname = get_filename(category, curr_time)
    try:
        driver.get(FORMAT_URL.format(category))
    except selenium.common.exceptions.WebDriverException as e:
        input("Something went wrong. Try resetting the network and hitting enter...")
        driver.get(FORMAT_URL.format(category))
    try:
        load_more_button = driver.find_element_by_class_name('load-more')
    except selenium.common.exceptions.NoSuchElementException:
        driver.quit()
        continue
    curr_html = None
    try:
        for i in range(MAX_CLICKS):
            if i % 10 == 0:
                #update curr_html in case of failure
                curr_html = driver.page_source
            click_failsafe(load_more_button)
            sys.stderr.write('\rLoading more... {0}/{1} ({2:.2f}%)'.format(i, MAX_CLICKS, i / MAX_CLICKS * 100))
            sys.stderr.flush()
    except:
        print("Exiting.")
        driver.quit()

    html_fname = 'output/html/{}.html'.format(fname)
    csv_fname = 'output/csv/{}.csv'.format(fname)
    with open(html_fname, 'wt') as f:
        f.write(curr_html)
        print("Saved html to {}".format(html_fname))

    soup = bsoup(curr_html, features='lxml')
    main_content = soup.findChild(class_ = 'main-content')
    article_previews = main_content.findChildren('article')
    parsed_previews = parse_article_previews(article_previews)

    writer_f = open(csv_fname, 'w')
    writer = csv.DictWriter(writer_f, fieldnames=HEADER)
    writer.writeheader()
    for row in parsed_previews:
        writer.writerow(row)
    writer_f.flush()
    writer_f.close()
    print("Saved csv to {}".format(csv_fname))
    print('Articles found: {}'.format(len(parsed_previews)))
