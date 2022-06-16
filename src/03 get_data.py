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

# # Creación del dataset
# Obtenemos los datos de 
# - **sensor** (que lo leemos del influxdb)
# - del registro de **movimientos realizados** por el robot
#
# Para unirlos y crear los dataset preparados para ser usados en Machine

# %load_ext autoreload
# %autoreload 2

import pandas as pd
from ut.base import save_df, time_from_str, FORMAT_UTC2, read_json
from utils import plot_one_var, crea_dataset, plot_one_move_var, procesa_all, une_datasets, process_one
from ut.timeSeries import to_ticked_time, get_tick
# genera un dataset para cada fichero en data_med y los almacena
procesa_all()

# Genera un dataset único con todos los dataset individuales
df_all, df_desc = une_datasets()

df_all

df_desc

# cuántos de cada uno
df_all[['pat', 'i', 'exp']].drop_duplicates().value_counts(['pat'])

# # 3. Visualización

# - `a` es **aceleración**  en unidades de g
# - `g` es **velocidad angular**, en unidades (de ??)
# - `c` (compas) es medida de **campo magnético **(en ??)
# - `f` **fusion**, angulos (pitch, roll, yaw)

variables = list(tot.variable.unique())

for v in variables:
    plot_one_move_var(tot, var=v, mov='A')

for v in variables:
    plot_one_move_var(tot, var=v, mov='B')

for v in variables:
    plot_one_move_var(tot, var=v, mov='C')

plot_one_move_var(tot, var='c0', mov='A', fa=3)
plot_one_move_var(tot, var='c0', mov='B', fa=3)
plot_one_move_var(tot, var='c0', mov='C', fa=3)

plot_one_move_var(tot, var='a0', mov='A', fa=3)
plot_one_move_var(tot, var='a0', mov='B', fa=3)
plot_one_move_var(tot, var='a0', mov='C', fa=3)
