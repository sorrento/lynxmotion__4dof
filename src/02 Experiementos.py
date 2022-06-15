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

# Realizamos secuecuencias de los patrones básicos (Un experimento

# %load_ext autoreload
# %autoreload 2

from lss import LSS, closeBus
from ut.roboticArm import Experimento, get_variables, init, home, resetea_all, apply_shift, range_of_base

di, l_base, l_hombro, l_codo, l_muneca, l_mano = init(go_home=True)

# +
# resetea_all(di)
# -

get_variables(di)

l_base.moveTo(00)

# # Creación de experimento

from ut.io import lista_files_recursiva
move_files = lista_files_recursiva('data_in/patrones/', 'json')

# +
# move_files
# -

# vamos a seleccionar 8 de estos
import random
move_files=random.sample(move_files,8)
move_files

exp = Experimento(di, 100, *move_files)

exp.get_patterns_used()

exp.get_sequence()

home(di)

# # PONER EL SENSOR
# 1. encenderlo (no se enciende luz) y amarrarlo
# 2. encender influxdb: ejecutable en `c:\Program Files\InfluxData\influxdb\influxdb2-2.1.1-windows-amd64\`
# 3. ejecutar el `/uart.py`. Se puede pinchar desde TotalCommander. pero si falla se borra. Mejor con Anaconda. O desde pycharm (ojo que parace que con python 3.8 se detiene después de un rato, mejor usar 3.9 
# 4. encender grafana  http://localhost:3000/ si se quere ver cómo va
#

# Para poner el sensor
home(di)
l_mano.moveTo(-400)
# l_codo.moveTo(-800)

# ### a) version normal

exp.run()

exp.save(name='Normal_10_pats_4', desc='No se paró, se ajustaron los tornillos para que no oscile',
         path='data_med/Experimentos/')

# ### b) version random

exp.set_random_perc(10)
exp.run(silent=True)

exp.save(name='Random_10_b', desc='Usando 10 moves base, con 10% de random',
         path='data_med/Experimentos/')

# ### c) version shifted

exp.set_random_perc(0)
exp.describe()

exp.run(range_shifted=900, silent=True)

exp.save(name='shifted_90_c', desc='shifted 90, sin random', 
         path='data_med/Experimentos/')

# ## REGENERA

exp.get_patterns_used()

exp.regenerate_sequence(10)

exp.get_sequence()

# # 9. Liberar el puerto

closeBus()
