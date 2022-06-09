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

# Creamos patrones de movimiento de manera aleatoria y los almacenamos
#

# %load_ext autoreload
# %autoreload 2

from lss import LSS, closeBus
from ut.roboticArm import Experimento, get_variables, init, home, resetea_all

di, l_base, l_hombro, l_codo, l_muneca, l_mano = init(go_home=False)

# +
# resetea_all(di)
# -

home(di)

get_variables(di)

# # Creación de experimento

from ut.io import lista_files_recursiva
move_files = lista_files_recursiva('data_in/patrones/', 'json')

# +
# move_files

# +
# Para poner el sensor
# home(di)
# l_mano.moveTo(-400)
# -

exp = Experimento(di, 3, *move_files)

exp.set_sequence(['R', 'M', 'Q'])

# ### a) version normal

exp.run()

exp.save(name='test_normal', desc='testing', path='data_med/Experimentos/')

# ### b) version random

get_variables(di)

exp.r_moves[0].get_df_moves()

# +
# get_variables(di)
# -

home(di)

exp.set_random_perc(5)
exp.run(silent=False)

exp.save(name='test_random5', desc='testing randomized', path='data_med/Experimentos/')

# ### c) version shifted

exp.run()

exp.save(name='test_normal', desc='testing', path='data_med/Experimentos/')

# # 9. Liberar el puerto

closeBus()
