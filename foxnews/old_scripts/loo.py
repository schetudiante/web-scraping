import numpy as np
import pandas as pd
from scipy import stats
import gensim
import sklearn.model_selection as cv
from sklearn.metrics import r2_score, make_scorer
from semantic_regression import SemanticRegression, SemanticRegressionVectors, SemanticRegressionSimple, SemanticRegressionWeighted
import matplotlib.pyplot as plt
import seaborn as sns

#Load in word vectors
vec_path = './vectors/{}/w2v_foxnews'.format(input('cbow/skipgram?: '))
word_vecs = gensim.models.Word2Vec.load(vec_path).wv

#Load in warmth/competence data
d0 = pd.read_csv('./input/wc/wc_ratings_unnormalized_typed.csv')
d1 = pd.read_csv('./input/wc/wc_validation2.csv')
d2 = pd.read_csv('./input/wc/wc_validation.csv')
data = pd.concat([d0, d1, d2], sort = False)

#Include only targets that are also inside the word_vec model
data = data.ix[[t in word_vecs for t in data.target]]

attribute = 'competence'


x = np.array(data.target)
X_vecs = word_vecs[x] #Store all the matching targets in word_vecs
y = np.array(data[attribute]) #Predicting category stored in attribute
y = np.log(y/100)-np.log(1-y/100)

model = SemanticRegressionVectors(word_vecs.syn0[:10000], ignore=5000, n_words=7500, n_best=50)
print('Fitting....')
model.fit(X_vecs, y)

model.predict(word_vecs['Trump'])

#TODO magic happens here: how does it predict attribute count from vectors?
model = SemanticRegressionVectors(word_vecs.syn0[:10000], ignore=5000, n_words=7500, n_best=50)

#Estimator, Data to be fit, Target variable to try to predict, Number of folds
#Using the semantic regression model, fitting to X_vecs, to predict y
# pred = cv.cross_val_predict(model, X_vecs, y, cv=len(X_vecs), verbose=1)
print(stats.linregress(pred, y)) #Outputs rvalue, intercept, slope, etc

model_text = SemanticRegression(word_vecs, ignore=5000, n_words=7500, n_best=20)
model_text.fit(x,y)
print(model_text.get_words())

# Adds name labels
def text_arr(xs, ys, tarr, **kwargs):
    for x, y, t in zip(xs, ys, tarr):
        plt.text(x, y, t, **kwargs)

plt.clf()
plt.scatter(pred, y)
plt.plot(y, y)
text_arr(pred,y,x)
plt.xlabel("predicted")
plt.ylabel("actual")
sns.despine(offset=10, trim=True)
plt.draw()
plt.show()
