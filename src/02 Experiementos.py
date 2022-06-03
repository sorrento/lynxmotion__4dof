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

import time
import pandas as pd
import lss
from u_base import get_now_format
from utils import Pattern, get_variables, plot_time, init, Experimento, home, test_move, move_from_files, resetea_all

di, l_base, l_hombro, l_codo, l_muneca, l_mano = init(go_home=True)

get_variables(di)

# # Creación de experimento

from u_io import lista_files_recursiva
move_files = lista_files_recursiva('data_in/', 'json')
# move_files

home(di)
l_mano.moveTo(-400)  # para poner el sensor

exp = Experimento(di, 3, *move_files)

exp.run()

# quitar tanto detalle y poner el nombre del patrón y el número  iterativo

exp.df

exp.d_moves_done

exp.save(name='fijos2', desc='eran 300 pero se apagó el BT parece')

# # 9. Liberar el puerto

lss.closeBus()
