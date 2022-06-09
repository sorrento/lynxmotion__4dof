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
from lss import closeBus
from ut.base import get_now_format
from utils import plot_time
from ut.roboticArm import Pattern, get_variables, init, test_move, move_from_files, test_all_moves
from ut.io import lista_files_recursiva

di, l_base, l_hombro, l_codo, l_muneca, l_mano = init(go_home=True)

get_variables(di)

# +
# recalibración, offset sde fábrica si hace falta
# home_definition(di, LSS_SetConfig)

# +
# l_mano.reset() # si se fuerza un servo, se bloquea (modo rojo parpadeante) y se debe resetear                       
# -

# # 2 Creación de movimientos [Aleatoriamente]

# Movimiento creado aleatoriamente
patt = Pattern(di, 'tt')
patt.create_random(n_moves=6, t_max=4)

patt

patt._run(test_mode=True, start_home=True)

patt.run(3, start_home=True, end_home=True, intercala_home=True)

patt.save()

# # 3 Cargamos los movimientos

move_files = lista_files_recursiva('data_in/patrones', 'json')
# move_files

pat = move_from_files(di, move_files, 'B')

# ### a) ejecución normal

res = pat.run()

res

# ### b) Con ruido

res = pat.run(random_perc=10)

res

# ### c) Con shift de base

# +
# resetea_all(di)
# -

res = pat.run(base_shift=900)

res

# +
# test_all_moves(move_files, di)
# -

# ## Corrección de un movimiento (que golpea la mesa)

m = move_from_files(di, move_files, 'B')
m.get_df_moves()

m.moves['3.14']['pos'] = 400
m.get_df_moves()

m.save()

m = test_move('B', move_files, di)

# # 8. Test de velocidades
#
# - Cogemos la información de velocidad el servo


# +
n = 4
ang = 600
velo = 20

i, co = 0, 0
con, li, nos = [], [], []
while i < n:
    k = pow(-1, i)
    l_base.moveTo(k * ang, velo)
    i = i + 1
    for k in range(40):
        v = int(l_base.getSpeed())
        no = get_now_format('%H:%M:%S.%f')
        li.append(v)
        time.sleep(0.01)  # máximo refresco es en torno a las centésimas de segundo
        co = co + 1
        con.append(co)
        nos.append(no)

    time.sleep(1)
vels = pd.DataFrame({'t': con, 'vel': li, 'time': nos})
# -

plot_time(vels, 'speed base, a 600')

plot_time(vels, 'speed base, a 100')

plot_time(vels, 'speed base, a 20')

# # Creación Manualmente

pat = Pattern(di, name='test')
pat.add('base', 0, -400, 100)
pat.add('codo', 0.5, -400, 10)
pat.add('codo', 2.9, -600, 100)
display(pat.get_df_moves())
pat.run(3)
pat.save()

# # 8. Verificación de Movimientos seguros

files = lista_files_recursiva('data_in/patrones/', 'json')

test_all_moves(files, di)

# # 9. Liberar el puerto

closeBus()
