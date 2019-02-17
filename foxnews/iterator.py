# -*- coding: utf-8 -*-
import csv
import os, os.path
import json
import re
from datetime import datetime
from nltk.tokenize import sent_tokenize, word_tokenize, WordPunctTokenizer

ignore_categories = {'food'}
ignore_domains = {'business'}

def clean(text):
    text = text.replace("\xa0", " ").replace('“', '"').replace('”', '"').replace('`', '\'')
    text.replace('\n', ' ')
    return text


class SentenceIterator(object):
    def __init__(self):
        self.dirname = '/home/chriskw/Research/nlp/fox/output/articles/'
        self.tokenizer = WordPunctTokenizer()

    def __iter__(self):
        with open('/home/chriskw/Research/nlp/foxnews/fox_data/fox.csv', 'rt') as f:
            reader = csv.DictReader(f)
            for row in reader:
                skip = False
                for val in [row['category']] + json.loads(row['tags'].replace("'", '"')):
                    for i in ignore_categories:
                        if i in val:
                            skip = True
                for ig_domain in ignore_domains:
                    if ig_domain in row['domain']:
                        skip = True
                if skip:
                    continue
                desc = row['description']
                desc = clean(desc)
                for sentence in sent_tokenize(desc):
                    yield sentence
                text = row['text']
                text = clean(text)
                for sentence in sent_tokenize(text):
                    yield sentence
