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
from utils import Pattern, get_variables, plot_time, init, Experimento, home, is_moving, patterns_from_files

di, l_base, l_hombro, l_codo, l_muneca, l_mano = init()

get_variables(di)

# +
# l_mano.reset() # si se fuerza un servo, se bloquea (modo rojo parpadeante) y se debe resetear                       
# -

# # 2 Aleatoriamente

# Movimiento creado aleatoriamente
pat_a = Pattern(di, 'V')
pat_a.create_random(n_moves=6, t_max=4)

pat_a._run(test_mode=True, start_home=True)

pat_a.run(3, start_home=True, end_home=True, intercala_home=True)

pat_a.save()

# # Cargamos los movimientos y los combinamos en secuencias

from u_io import lista_files_recursiva

move_files = lista_files_recursiva('data_in/', 'json')
move_files


def test_move(move, files, di):
    p = move_from_files(di, files, move)
    p.run(end_home=False)
    return p


def move_from_files(di, files, move):
    pats = patterns_from_files(di, files)
    return [x for x in pats if x.name == move][0]


def test_all_moves(files, di):
    pats = patterns_from_files(di, files)
    for mo in pats:
        print('\n\n>>>>>>>>>>>>>>>>>>> ', mo.name)
        mo.run(start_home=True, end_home=True)


test_all_moves(move_files, di)

# ## Corrección de un movimiento (que golpea la mesa)

m = move_from_files(di, move_files, 'B')
m.get_df()

m.moves['3.14']['pos'] = 400
m.get_df()

m.save()

m = test_move('B', move_files, di)

# # Creación de experimento

exp = Experimento(di, 2, *move_files)

exp.run()

exp.df

exp.save(name='test2', desc='para test')

tx='experimentoe 1'+ '\n' +str([x.name for x in exp.r_moves])

exp.df

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

# # 1. Manualmente

pat = Pattern(di, name='test')
pat.add('base', 0, -400, 100)
pat.add('codo', 0.5, -400, 10)
pat.add('codo', 2.9, -600, 100)
display(pat.get_df())
pat.run(3)
pat.save()

# # 9. Liberar el puerto

lss.closeBus()
