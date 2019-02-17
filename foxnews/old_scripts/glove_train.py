# -*- coding: utf-8 -*-
from glove import Glove, Corpus
import logging
import os, os.path
import re
import sys
from datetime import datetime
from nltk.tokenize import sent_tokenize, word_tokenize, WordPunctTokenizer


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

OUTPUT_DIR = './vectors/glove_test/'
DATE_REGEX = re.compile(r'_\d\d\d\d_\d\d_\d\d_')
ANNOUNCEMENT_DATE = datetime(2015, 6, 16)
ELECTION_DATE = datetime(2016, 11, 9)

def get_date(fname):
    matches = re.findall(DATE_REGEX, fname)
    if matches:
        try:
            match = map(int, matches[0][1:-1].split('_'))
            return datetime(*match)
        except:
            print('Error when parsing date for: {}'.format(fname))
    return ''

class SentencesIterator(object):
    def __init__(self, dirname):
        self.dirname = dirname
        self.tokenizer = WordPunctTokenizer()

    def __iter__(self):
        for fname in os.listdir(self.dirname):
            sys.stdout.flush()
            sys.stdout.write('Reading from: {}\r'.format(fname[:80]))
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
                yield self.tokenizer.tokenize(sent)

dirname = os.path.expanduser('./output/articles')

sentences = SentencesIterator(dirname)
print('Building Corpus...')
corpus_model = Corpus()
corpus_model.fit(sentences, window=10)
corpus_model.save(OUTPUT_DIR + 'corpus.model')
print('Build and saved!')
print('Dict size: %s' % len(corpus_model.dictionary))
print('Collocations: %s' % corpus_model.matrix.nnz)
print('Training the GloVe model')

glove = Glove(no_components=300, learning_rate=0.05)
glove.fit(corpus_model.matrix, epochs=25,
          no_threads=10, verbose=True)
glove.add_dictionary(corpus_model.dictionary)

glove.save(OUTPUT_DIR + 'glove.model')
# model = gensim.models.Word2Vec(sentences, size=300, min_count=5, iter=10, workers=10, sg=1)
# model.save('./vectors/trump_preprocess_skipgram/w2v_foxnews')
