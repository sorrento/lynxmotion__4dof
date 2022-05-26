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
import pandas as pd
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient

from config import ORG, TOKEN
from u_base import FORMAT_DATETIME, FORMAT_UTC, save_df
from utils import make_query, plot_one_var, crea_dataset

# -

# # 1 Lectura de los datos de Influx para un experimento

df = pd.read_csv('data/exp_test20220525_124118__20220525_125036.csv')

t0 = datetime.strptime(df.time.iloc[0], FORMAT_DATETIME)
t1 = datetime.strptime(df.time.iloc[-1], FORMAT_DATETIME)
t1 = t1 + timedelta(seconds=2)
t0, t1

# apaño: le restamos 2 horas porque este df no fue generado con hora utc
t0 = t0 + timedelta(hours=-2)
t1 = t1 + timedelta(hours=-2)
t0, t1

client = InfluxDBClient(url="http://localhost:8086", token=TOKEN, org=ORG)
query_api = client.query_api()

q = make_query(t0.strftime(FORMAT_UTC), t1.strftime(FORMAT_UTC))
dataframe = query_api.query_data_frame(q)

dt = dataframe[['_field', '_value', '_time']]
save_df(dt, 'data', 'measu_''test20220525_124118__20220525_125036')

plot_one_var(dt, 'a0')

# # Cortamos por partes

df = pd.read_csv('data/exp_test20220525_124118__20220525_125036.csv')
df['i'] = df.index + 1
df = df.set_index('i')  # todo guardar ya con índicd desde 1
df

dt = pd.read_csv('data/measu_test20220525_124118__20220525_125036_73k_3.csv')
dt

tot = crea_dataset(dt, df)

tot

save_df(tot, path='data', name='exp1', append_size=False)  # todo homogenizar nombres
