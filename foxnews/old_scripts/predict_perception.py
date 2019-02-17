import numpy as np
import pandas as pd
from scipy import stats
import gensim
import sklearn.model_selection as cv
from sklearn.metrics import r2_score, make_scorer
from sklearn.linear_model import Lasso, Ridge
import re
from pprint import pprint
import os.path
import csv
from wordvec_utils import check_presence, get_wordvecs, loo_r2_score

vec_path = './vectors/{}/w2v_foxnews'.format(input('Which model? (cbow, skipgram): '))
csv_path = './output/wc_predict.csv'
word_vecs = gensim.models.Word2Vec.load(vec_path).wv

vec_name = os.path.basename(vec_path)
word_vecs.init_sims()


d1 = pd.read_csv('./input/wc/wc_validation_counts.csv')
d2 = pd.read_csv('./input/wc/wc_validation2_counts.csv')
data = pd.concat([d1, d2])
data = data.ix[[t != 'state' for t in data['type']]]

data = data.ix[[check_presence(t, word_vecs) for t in data.target]]

print(len(data))

models = {}
for attribute in ['warmth', 'competence']:
    x = np.array(data.target)
    X_vecs = get_wordvecs(x, word_vecs, normalize=True)
    y = np.array(data[attribute])

    alphas = np.exp(-np.linspace(0,10,40))
    r2s = []
    for alpha in alphas:
        model = Ridge(alpha=alpha)
        r2 = loo_r2_score(model, X_vecs, y)
        r2s.append(r2)

    alpha = alphas[np.argmax(r2s)]
    print(alpha)

    # for typ in list(np.unique(data['type'])) + ['all']:
    typ = 'all'
    if typ == 'all':
        dd = data
    else:
        dd = data.ix[data['type'] == typ]

    x = np.array(dd.target)
    X_vecs = get_wordvecs(x, word_vecs, normalize=True)
    y = np.array(dd[attribute])

    model = Ridge(alpha=alpha)
    models[attribute] = model
    pred = cv.cross_val_predict(model, X_vecs, y, cv=len(x))
    # s = stats.linregress(y, pred)
    # print(s)

    print('\n{} {} {} {}'.format(vec_name, attribute, typ, len(dd)))

    print(r2_score(y, pred))

    model.fit(X_vecs, y)

    #Takes coeffecients of the regression model and compares to most similar vectors
    vec = model.coef_
    vec /= np.linalg.norm(vec)
    #converts to unit vec
    pprint(word_vecs.similar_by_vector(vec, topn=5))
    pprint(word_vecs.similar_by_vector(-vec, topn=5))

def normalize(arr):
    return (arr - np.mean(arr)) / np.std(arr)

targets = ['Democrat', 'Republican', 'immigrant', 'American', 'Mexican', 'British',\
           'Jewish', 'Russian', 'Muslim', 'Obama', 'Trump', 'Clinton', 'antifa',\
           'astrologer', 'astronaut']
vecs = list(map(lambda t: word_vecs[t], targets))
warmth = models['warmth'].predict(vecs)
warmth_norm = normalize(warmth)
competence = models['competence'].predict(vecs)
competence_norm = normalize(competence)
with open(csv_path, 'wt') as f:
    writer = csv.writer(f)
    writer.writerow(['target', 'warmth', 'competence', 'warmth_norm', 'competence_norm'])
    for row in zip(targets, warmth, competence, warmth_norm, competence_norm):
        print(row)
        writer.writerow(row)
