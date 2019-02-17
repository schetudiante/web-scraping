# -*- coding: utf-8 -*-
import os, os.path
import re
from datetime import datetime
from nltk.tokenize import sent_tokenize, word_tokenize, WordPunctTokenizer

DATE_REGEX = re.compile(r'_\d\d\d\d_\d\d_\d\d_')
ANNOUNCEMENT_DATE = datetime(2015, 6, 16)
ELECTION_DATE = datetime(2016, 11, 9)
acceptable_singles = '1234567890ia'
def get_date(fname):
    matches = re.findall(DATE_REGEX, fname)
    if matches:
        try:
            match = map(int, matches[0][1:-1].split('_'))
            return datetime(*match)
        except:
            print('Error when parsing date for: {}'.format(fname))
    return ''

class SentenceIterator(object):
    def __init__(self):
        self.dirname = '/home/chris/Research/nlp/fox/output/articles/'
        self.tokenizer = WordPunctTokenizer()

    def __iter__(self):
        for fname in os.listdir(self.dirname):
            date = get_date(fname)
            with open(os.path.join(self.dirname, fname), 'r') as f:
                text = f.read()
            text = text.replace('Donald Trump', 'Donald_Trump')
            text = text.replace('Melania Trump', 'Melania_Trump')
            text = text.replace('Ivanka Trump', 'Ivanka_Trump')
            text = text.replace('Eric Trump', 'Eric_Trump')
            if date and date < ANNOUNCEMENT_DATE:
                text = text.replace('Trump', 'Trump_Pre_Campaign')
            elif date and date < ELECTION_DATE:
                text = text.replace('Trump', 'Trump_Pre_Election')
            elif date and date >= ELECTION_DATE:
                text = text.replace('Trump', 'Trump_Post_Election')

            text = text.replace("\xa0", " ").replace('“', '"').replace('”', '"')
            sents = sent_tokenize(text)
            for sent in sents:
                yield sent
