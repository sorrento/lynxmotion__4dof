# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %load_ext autoreload
# %autoreload 2

# +
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf

from u_ml import standardize_function, Classifier
from utils import plot_umaps
# -

print(tf.__version__)

tf.config.list_physical_devices('CPU')

tf.config.list_physical_devices('GPU')

# !nvidia-smi

npath = 'data_out/'
df = pd.read_csv(npath + 'exp1.csv')
df

# dataset horizontal y completar nan con interpolación
dfa = df.groupby(['i', 'tt', 'move', '_field']).agg('_value').mean().reset_index()
dfp = dfa.pivot(index=['i', 'tt', 'move'], columns=['_field'], values='_value').reset_index()
dfp1 = dfp.groupby(['i']).apply(lambda group: group.interpolate())
dfp1 = dfp1.fillna(0)
dfp1['class'] = dfp1.move.astype('category').cat.codes
dfp1

# # 1. UMAP 

import umap
features = list(set(dfp1.columns) - {'_field', 'i', 'tt', 'move', 'class'})
datas = standardize_function(dfp1[features])
datas

# ## a) a pelo

reducer = umap.UMAP(verbose=True)
embedding = reducer.fit_transform(datas)

plot_umaps(embedding, dfp1)

# ## b) supervisado

reducer2 = umap.UMAP(verbose=True)
embedding2 = reducer.fit_transform(datas, y=dfp1['class'])

plot_umaps(embedding2, dfp1)

dfp

# get last 58 timestamps excluding group 100  #### WHY 57?
dfp2 = dfp1[dfp1.i != 100]
dfp2 = dfp2.groupby("i").apply(lambda x: x.iloc[-57:])
dfp2 = dfp2.rename(columns={'i': 'ii'})
dfp2

dfp2.groupby('ii').count()['tt'].plot()

target = np.asarray(pd.get_dummies(dfp2['class'].values)).reshape((-1, 57, 3))
target.shape

target[1]

data = np.asarray(dfp2[features]).reshape((-1, 57, 12))
data.shape

data[1]  # tensor

X_train, y_train = data[:60], target[:60]
X_val, y_val = data[60:80], target[60:80]
X_test, y_test = data[80:], target[80:]

# +
LR = .001  # learning rate
nn_epochs = 15
nn_batch_size = 16

shape_ = (None, X_train.shape[2])  # input is going to be the number of feature we are using (dimension 2 of 0, 1, 2)
n_out = 3
model = Classifier(shape_, n_out, LR)

# +
model.fit(X_train, y_train,
          epochs=nn_epochs,
          batch_size=nn_batch_size, verbose=2,
          validation_data=(X_val, y_val))

preds_test = model.predict(X_test)
# -

# Ha acertado 100%:

preds_test.shape

np.mean(preds_test, axis=1)

l_pred=np.argmax(np.mean(preds_test, axis=1), axis=1)
l_pred

l_test=np.argmax(np.mean(y_test, axis=1), axis=1)
l_test

import u_ml as u

u.pinta_cm2(l_test, l_pred, ['A', 'B', 'C'])

y_test
