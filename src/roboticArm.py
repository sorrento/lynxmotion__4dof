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

import time
import pandas as pd
import lss
from u_base import get_now_format
from utils import Pattern, get_variables, plot_time, init,  Experimento

di, l_base, l_hombro, l_codo, l_muneca, l_mano = init()

get_variables(di)

# +
# l_mano.reset() # si se fuerza un servo, se bloquea (modo rojo parpadeante) y se debe resetear                       
# -

# # Creamos un patrón, es decir un movimiento compuesto

pat = Pattern(di, name='test')
pat.add('base', 0, -400, 100)
pat.add('codo', 0.5, -400, 10)
pat.add('codo', 2.9, -600, 100)
display(pat.get_df_moves())
pat.run(3)
pat.save()

# Movimiento creado aleatoriamente
pat_a = Pattern(di, 'A')
pat_a.create_random(n_moves=6, t_max=4)
pat_a.run(3)
pat_a.save()

pat_b = Pattern(di, 'B')
pat_b.create_random(n_moves=4, t_max=4)
pat_b.run(3)
pat_b.save()

# # Cargamos los movimientos y los combinamos en secuencias

exp = Experimento(di, 100, 'data/move_A.json', 'data/move_B.json', 'data/move_C.json')

exp.run()

exp.save(name='test')

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

# # 9. Liberar el puerto

lss.closeBus()
