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
from utils import home, pattern, get_variables, plot_time, init

di, l_base, l_hombro, l_codo, l_muneca, l_mano = init()

get_variables(di)

# +
# l_mano.reset() # si se fuerza un servo, se bloquea (modo rojo parpadeante) y se debe resetear                       
# -

# # 2. Generar movimientos compuestos
#
# - controlar las velocidades
# - controlar cuándo se realiza un movimiento (al solaparse)
# - mover no sólo de manera relativa, sino absoluta (posición final)


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

# # Creamos un patrón, es decir un movimiento compuesto

pat = pattern(di, name='test')
pat.add('base', 0, -400, 100)
pat.add('codo', 0.5, -400, 10)
pat.add('codo', 2.9, -600, 100)
display(pat.get_df())
pat.run(3)
pat.save()

# Movimiento creado aleatoriamente
pat_a = pattern('A')
pat_a.create_random(n_moves=4, t_max=4)
pat_a.run(3)
pat_a.save()


pat_b = pattern('B')
pat_b.create_random(n_moves=4, t_max=4)
pat_b.run(3)
pat_b.save()

pat_a = pattern('C')
pat_a.create_random(n_moves=4, t_max=4)
pat_a.run(3)
pat_a.save()



# # 9. Liberar el puerto

lss.closeBus()