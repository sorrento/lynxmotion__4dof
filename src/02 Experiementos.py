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

from ut import lss
from ut.roboticArm import Experimento, get_variables, init

di, l_base, l_hombro, l_codo, l_muneca, l_mano = init(go_home=True)

get_variables(di)

# # Creación de experimento

from ut.io import lista_files_recursiva
move_files = lista_files_recursiva('data_in/', 'json')

# +
# move_files

# +
# home(di)
# l_mano.moveTo(-400)  # para poner el sensor
# -

exp = Experimento(di, 3, *move_files)

exp.run()

exp.save(name='Test_fijo', desc='testing', path='data_med/Experimentos/')

# # 9. Liberar el puerto

lss.closeBus()
