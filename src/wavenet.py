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

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.layers import Conv1D, Input, Dense, Add, Multiply
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import losses, models, optimizers

print(tf.__version__)

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

# +
import umap
from sklearn.preprocessing import StandardScaler, MinMaxScaler


def standardize_function(X_train):
    df_scaled = pd.DataFrame(StandardScaler().fit_transform(X_train), columns=X_train.columns)
    return df_scaled


features = list(set(dfp1.columns) - {'_field', 'i', 'tt', 'move', 'class'})
datas = standardize_function(dfp1[features])
datas
# -

# ## a) a pelo

reducer = umap.UMAP(verbose=True)
embedding = reducer.fit_transform(datas)

plt.figure(figsize=(20, 20))
for i, v in enumerate(['tt', 'class']):
    plt.subplot(2, 2, i + 1)
    plt.scatter(
        embedding[:, 0],
        embedding[:, 1],
        c=dfp1[v].values, s=1, alpha=1)
    plt.gca().set_aspect('equal', 'datalim')
    plt.title(v, fontsize=24)

# ## b) supervisado

dfp1

reducer2 = umap.UMAP(verbose=True)
embedding2 = reducer.fit_transform(datas, y=dfp1['class'])

plt.figure(figsize=(20, 20))
for i, v in enumerate(['tt', 'class']):
    plt.subplot(2, 2, i + 1)
    plt.scatter(
        embedding2[:, 0],
        embedding2[:, 1],
        c=dfp1[v].values, s=1, alpha=1)
    plt.gca().set_aspect('equal', 'datalim')
    plt.title(v, fontsize=24)

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

data[1] # tensor

X_train, y_train = data[:60], target[:60]
X_val, y_val = data[60:80], target[60:80]
X_test, y_test = data[80:], target[80:]


def Classifier(shape_, n_out):
    def wave_block(x, filters, kernel_size, n):
        dilation_rates = [2 ** i for i in range(n)]
        x = Conv1D(filters=filters,
                   kernel_size=1,
                   padding='same')(x)
        res_x = x
        for dilation_rate in dilation_rates:
            tanh_out = Conv1D(filters=filters,
                              kernel_size=kernel_size,
                              padding='same',
                              activation='tanh',
                              dilation_rate=dilation_rate)(x)
            sigm_out = Conv1D(filters=filters,
                              kernel_size=kernel_size,
                              padding='same',
                              activation='sigmoid',
                              dilation_rate=dilation_rate)(x)
            x = Multiply()([tanh_out, sigm_out])
            x = Conv1D(filters=filters,
                       kernel_size=1,
                       padding='same')(x)
            res_x = Add()([res_x, x])
        return res_x

    inp = Input(shape=(shape_))

    x = wave_block(inp, 16, 3, 12)
    x = wave_block(x, 32, 3, 8)
    x = wave_block(x, 64, 3, 4)
    x = wave_block(x, 128, 3, 1)

    out = Dense(n_out, activation='softmax', name='out')(x)

    model = models.Model(inputs=inp, outputs=out)

    opt = Adam(lr=LR)
    # opt = tfa.optimizers.SWA(opt)
    model.compile(loss=losses.CategoricalCrossentropy(), optimizer=opt, metrics=['accuracy'])
    return model


# +
LR = .001
nn_epochs = 15
nn_batch_size = 16

shape_ = (None, X_train.shape[2])  # input is going to be the number of feature we are using (dimension 2 of 0, 1, 2)
n_out = 3
model = Classifier(shape_, n_out)


# +
model.fit(X_train, y_train,
          epochs=nn_epochs,
          batch_size=nn_batch_size, verbose=2,
          validation_data=(X_val, y_val))

preds_test = model.predict(X_test)
# -

# Ha acertado 100%:

np.argmax(np.mean(preds_test, axis=1), axis=1)

np.argmax(np.mean(y_test, axis=1), axis=1)
