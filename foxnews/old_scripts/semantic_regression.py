from scipy import stats
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.externals.joblib import Parallel, delayed
import numpy as np
import random
from sklearn.linear_model import LinearRegression, TheilSenRegressor, RANSACRegressor, HuberRegressor
import copy

def get_top_corr_raw(X, the_vec, vecs, n_samples=1, category=None):
    # vecs = word_vecs.syn0[:topn]

    y_pred = vecs.dot(X.T)

    y_pred -= np.mean(y_pred,axis=1)[:, np.newaxis]
    y_pred /= np.linalg.norm(y_pred, axis=1)[:, np.newaxis]

    y_actual = the_vec - np.mean(the_vec)
    y_actual /= np.linalg.norm(y_actual)

    ixs = range(y_pred.shape[1])


    if n_samples == 1:
        sample_size = len(ixs)
    else:
        sample_size = int(len(ixs)*(2/3))

    samples = []

    if category is not None:
        category = np.array(category)
        for typ in np.unique(category):
            samp = np.where(category==typ)[0]
            samples.append(np.array(samp))
        samples.append(ixs)

    for i in range(n_samples):
        samp = random.sample(ixs, sample_size)
        samples.append(np.array(samp))

    rs = 0
    for samp in samples:
        rs += y_pred[:, samp].dot(y_actual[samp])
    rs /= len(samples)

    return np.array(rs)

def get_top_corr(X, y, vecs, n_samples=1, n_words=10000, n_jobs=1, category=None):
    n_rows = n_words/float(n_jobs)

    ixs = list(range(0,n_words-1,int(n_rows)))
    ixs.append(n_words)

    results = Parallel(n_jobs=n_jobs)(
        delayed(get_top_corr_raw)(X, y, vecs[start:end], n_samples,
                                  category=category)
                for start,end in zip(ixs, ixs[1:]))

    return np.hstack(results)



class SemanticRegression(BaseEstimator, RegressorMixin):
    """Semantic regression class.

    The aim of semantic regression is to map categorical
    labels (e.g. brands, countries, etc) to values (e.g. brand value, log GDP of
    country, etc). We do this by mapping the labels to values using word embeddings, and then doing regression on the word embeddings.
    To do "regression", we

    Parameters
    ----------
    word_vecs: The word vectors to use for regression. Should be an instance of gensim.models.keyedvectors.KeyedVectors
    n_samples: Number of samples to use for better estimation of best words (default is 1 sample)
    n_words: How many of the most frequent words to correlate with the metric
    n_best: How many of the top correlated words to use in prediction
    """

    def __init__(self, word_vecs, n_samples=1, n_words=7500, n_best=50, ignore=5000, n_jobs=1):
        self.word_vecs = word_vecs
        self.n_samples = n_samples
        self.n_words = n_words
        self.n_best = n_best
        self.n_jobs = n_jobs
        self.ignore = ignore
        self.vecs = np.array(word_vecs.syn0[:n_words])

    def fit(self, X, y, category=None):
        X_vecs = self.word_vecs[X]
        rs = get_top_corr(X_vecs, y, vecs=self.vecs,
                          n_samples=self.n_samples, n_words=self.n_words,
                          n_jobs=self.n_jobs, category=category)
        rs[:self.ignore] = 0
        ixs = np.argsort(-rs)
        if self.n_best < 1:
            pos = self.vecs[rs > self.n_best]
            neg = self.vecs[rs < -self.n_best]
            if pos.shape[0] == 0 and neg.shape[0] == 0:
                self._coef = self.vecs[ixs[0]] - self.vecs[ixs[-1]]
            elif pos.shape[0] == 0:
                self._coef = np.mean(neg,axis=0)
            elif neg.shape[0] == 0:
                self._coef = np.mean(pos,axis=0)
            else:
                self._coef = np.mean(pos,axis=0) - np.mean(neg,axis=0)
            self._pos_ixs = ixs[rs > self.n_best]
            self._neg_ixs = ixs[rs < -self.n_best]
        else:

            self._pos_ixs = ixs
            self._neg_ixs = ixs[::-1]
            pos = np.mean(self.vecs[self._pos_ixs[:self.n_best]], axis=0)
            neg = np.mean(self.vecs[self._neg_ixs[:self.n_best]], axis=0)
            self._coef = pos - neg

        pred = X_vecs.dot(self._coef)
        s = stats.linregress(pred, y)
        self._reg = HuberRegressor()
        self._reg.fit(pred[:, np.newaxis], y)
        self._slope = s.slope
        self._intercept = s.intercept
        return self

    def predict(self, X):
        vecs = self.word_vecs[X]
        pred = vecs.dot(self._coef)
        # pred_corr = pred * self._slope + self._intercept
        pred_corr = self._reg.predict(pred[:, np.newaxis])
        return pred_corr

    def get_words(self, n_best=None):
        if n_best is None:
            n_best = self.n_best
        if n_best < 1:
            pos_words = [self.word_vecs.index2word[i] for i in self._pos_ixs]
            neg_words = [self.word_vecs.index2word[i] for i in self._neg_ixs]
        else:
            pos_words = [self.word_vecs.index2word[i] for i in self._pos_ixs[:n_best]]
            neg_words = [self.word_vecs.index2word[i] for i in self._neg_ixs[:n_best]]
        return np.array(pos_words), np.array(neg_words)

    def fit_predict(self, X, y):
        return self.fit(X, y).predict(X)


class SemanticRegressionVectors(BaseEstimator, RegressorMixin):
    """Semantic regression class.

    The aim of semantic regression is to map categorical
    labels (e.g. brands, countries, etc) to values (e.g. brand value, log GDP of
    country, etc). We do this by mapping the labels to values using word embeddings, and then doing regression on the word embeddings.
    To do "regression", we

    Parameters
    ----------
    word_vecs: The word vectors to use for regression. Should be an instance of gensim.models.keyedvectors.KeyedVectors
    n_samples: Number of samples to use for better estimation of best words (default is 1 sample)
    n_words: How many of the most frequent words to correlate with the metric
    n_best: How many of the top correlated words to use in prediction
    """

    def __init__(self, vecs, n_samples=1, n_words=7500, n_best=5, ignore=1000, n_jobs=1):
        self.n_samples = n_samples
        self.n_words = n_words
        self.n_best = n_best
        self.n_jobs = n_jobs
        self.ignore = ignore
        self.vecs = vecs

    def fit(self, X, y, category=None):
        rs = get_top_corr(X, y, vecs=self.vecs[:self.n_words],
                          n_samples=self.n_samples, n_words=self.n_words,
                          n_jobs=self.n_jobs, category=category)
        rs[:self.ignore] = 0
        ixs = np.argsort(-rs)
        if self.n_best < 1:
            pos = self.vecs[rs > self.n_best]
            neg = self.vecs[rs < -self.n_best]
            self._pos_ixs = ixs[rs > self.n_best]
            self._neg_ixs = ixs[rs < -self.n_best]

            #self._coef gets set here
            if pos.shape[0] == 0 and neg.shape[0] == 0:
                self._coef = self.vecs[ixs[0]] - self.vecs[ixs[-1]]
            elif pos.shape[0] == 0:
                self._coef = np.mean(neg,axis=0)
            elif neg.shape[0] == 0:
                self._coef = np.mean(pos,axis=0)
            else:
                self._coef = np.mean(pos,axis=0) - np.mean(neg,axis=0)
        else:

            self._pos_ixs = ixs
            self._neg_ixs = ixs[::-1]
            pos = np.mean(self.vecs[self._pos_ixs[:self.n_best]], axis=0)
            neg = np.mean(self.vecs[self._neg_ixs[:self.n_best]], axis=0)
            self._coef = pos - neg

        pred = X.dot(self._coef)
        s = stats.linregress(pred, y)
        self._reg = HuberRegressor()
        self._reg.fit(pred[:, np.newaxis], y)
        self._slope = s.slope
        self._intercept = s.intercept
        return self

    #X := input vector
    def predict(self, X):
        pred = X.dot(self._coef)
        pred_corr = pred * self._slope + self._intercept
        # pred_corr = self._reg.predict(pred[:, np.newaxis])
        return pred_corr

    def get_words(self, n_best=None):
        if n_best is None:
            n_best = self.n_best
        if n_best < 1:
            pos_words = self._pos_ixs
            neg_words = self._neg_ixs
        else:
            pos_words = self._pos_ixs[:n_best]
            neg_words = self._neg_ixs[:n_best]
        return np.array(pos_words), np.array(neg_words)


    def transfer_model(self, word_vecs_current, word_vecs_new, x):
        pos_ix, neg_ix = self.get_words()
        words = np.array(word_vecs_current.index2word)
        w_pos = [w for w in words[pos_ix] if w in word_vecs_new]
        w_neg = [w for w in words[neg_ix] if w in word_vecs_new]

        model_new = copy.copy(self)

        model_new.vecs = word_vecs_new.syn0

        pos_new = np.mean(word_vecs_new[w_pos], axis=0)
        neg_new = np.mean(word_vecs_new[w_neg], axis=0)
        model_new._coef = pos_new - neg_new

        pred_curr = word_vecs_current[x].dot(self._coef)
        pred_new = word_vecs_new[x].dot(model_new._coef)

        reg2 = HuberRegressor()
        reg2.fit(pred_new[:, np.newaxis], pred_curr)

        # a(a'*x + b')+b
        # a*a' * x + a*b' + b

        model_new._reg.coef_ = reg2.coef_ * self._reg.coef_
        model_new._reg.intercept_ = self._reg.coef_ * reg2.intercept_ + self._reg.intercept_

        return model_new

    def fit_predict(self, X, y):
        return self.fit(X, y).predict(X)


class SemanticRegressionWeighted(BaseEstimator, RegressorMixin):
    """Semantic regression class.

    The aim of semantic regression is to map categorical
    labels (e.g. brands, countries, etc) to values (e.g. brand value, log GDP of
    country, etc). We do this by mapping the labels to values using word embeddings, and then doing regression on the word embeddings.
    To do "regression", we

    Parameters
    ----------
    word_vecs: The word vectors to use for regression. Should be an instance of gensim.models.keyedvectors.KeyedVectors
    n_samples: Number of samples to use for better estimation of best words (default is 1 sample)
    n_words: How many of the most frequent words to correlate with the metric
    n_best: How many of the top correlated words to use in prediction
    """

    def __init__(self):
        pass

    def fit(self, X, y, category=None):
        weights = y - np.mean(y)
        weights = weights / np.max(np.abs(weights))
        self._coef = np.mean(X*weights[:, np.newaxis], axis=0)
        pred = X.dot(self._coef)
        # s = stats.linregress(pred, y)
        self._reg = HuberRegressor(epsilon=1.10)
        self._reg.fit(pred[:, np.newaxis], y)
        # self._slope = s.slope
        # self._intercept = s.intercept
        return self

    def predict(self, X):
        pred = X.dot(self._coef)
        # pred_corr = pred * self._slope + self._intercept
        pred_corr = self._reg.predict(pred[:, np.newaxis])
        return pred_corr

    def fit_predict(self, X, y):
        return self.fit(X, y).predict(X)


class SemanticRegressionSimple(BaseEstimator, RegressorMixin):
    """Semantic regression class.

    The aim of semantic regression is to map categorical
    labels (e.g. brands, countries, etc) to values (e.g. brand value, log GDP of
    country, etc). We do this by mapping the labels to values using word embeddings, and then doing regression on the word embeddings.
    To do "regression", we

    Parameters
    ----------
    word_vecs: The word vectors to use for regression. Should be an instance of gensim.models.keyedvectors.KeyedVectors
    n_samples: Number of samples to use for better estimation of best words (default is 1 sample)
    n_words: How many of the most frequent words to correlate with the metric
    n_best: How many of the top correlated words to use in prediction
    """

    def __init__(self, n_top=2):
        self.n_top = n_top

    def fit(self, X, y, category=None):
        ixs = np.argsort(y)
        self._coef = np.mean(X[ixs[:self.n_top]] - X[ixs[-self.n_top:]], axis=0)
        pred = X.dot(self._coef)
        # s = stats.linregress(pred, y)
        self._reg = HuberRegressor()
        self._reg.fit(pred[:, np.newaxis], y)
        # self._slope = s.slope
        # self._intercept = s.intercept
        return self

    def predict(self, X):
        pred = X.dot(self._coef)
        # pred_corr = pred * self._slope + self._intercept
        pred_corr = self._reg.predict(pred[:, np.newaxis])
        return pred_corr

    def fit_predict(self, X, y):
        return self.fit(X, y).predict(X)
