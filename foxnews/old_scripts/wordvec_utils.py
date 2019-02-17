import gensim
import numpy as np
import sklearn.model_selection as cv
from sklearn.metrics import r2_score, make_scorer

def check_presence(word, word_vecs, lower=False):
    for w in word.split(' '):
        if lower:
            w = w.lower()
        if w not in word_vecs:
            return False
    return True

def get_wordvecs(words, word_vecs, normalize=True, lower=False):
    vecs = []
    for word in words:
        vec = 0 * word_vecs[word_vecs.index2word[0]]
        if lower:
            word = word.lower()
        for w in word.split(' '):
            vec += word_vecs[w]
        vecs.append(vec)
    vecs = np.array(vecs)
    if normalize:
        vecs = vecs / np.linalg.norm(vecs, axis=1)[:, np.newaxis]
    return vecs

def normalize(target):
    return '_'.join([t.capitalize() for t in target.split(' ')])

def loo_r2_score(model, X, y):
    pred = cv.cross_val_predict(model, X, y, cv=len(X))
    return r2_score(y, pred)

