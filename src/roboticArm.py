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
import lss_const
from u_base import get_now_format
from utils import home, pattern, reset, get_variables, plot_time


def init():
    global di, l_base, l_hombro, l_codo, l_muneca, l_mano
    CST_LSS_Port = "COM5"  # Use the app LSS Flowarm that makes automatic scanning
    CST_LSS_Baud = lss_const.LSS_DefaultBaud

    lss.initBus(CST_LSS_Port, CST_LSS_Baud)

    l_base = lss.LSS(1)
    l_hombro = lss.LSS(2)
    l_codo = lss.LSS(3)
    l_muneca = lss.LSS(4)
    l_mano = lss.LSS(5)

    l_base.setColorLED(lss_const.LSS_LED_Red)
    l_hombro.setColorLED(lss_const.LSS_LED_Blue)
    l_codo.setColorLED(lss_const.LSS_LED_Green)
    l_muneca.setColorLED(lss_const.LSS_LED_White)
    l_mano.setColorLED(lss_const.LSS_LED_Cyan)

    di = {'base':   {'o': l_base},
          'hombro': {'o': l_hombro},
          'codo':   {'o': l_codo},
          'muneca': {'o': l_muneca},
          'mano':   {'o': l_mano},
          }

    home(di)


init()

get_variables(di)

# +
# l_mano.reset() # si se fuerza un servo, se bloquea (modo rojo parpadeante) y se debe resetear                       
# -

# # 2. Generar movimientos compuestos
#
# - controlar las velocidades
# - controlar cuándo se realiza un movimiento (al solaparse)
# - mover no sólo de manera relativa, sino absoluta (posición final)


home(di)

n = 2
i = 0
while i < n:
    display(i)
    k = pow(-1, i)
    l_codo.moveTo(k * 200)
    #     time.sleep(0.051)
    l_base.moveTo(k * 200)
    i = i + 1
    time.sleep(1)
home(di)

home(di)

# # Control de velocidad

l_base.setMaxSpeed(40)

# +
n = 4
ang = 600
velo=20

i = 0
co = 0
con = []
li = []
nos = []
while i < n:
    #     display(i)
    k = pow(-1, i)
    #     l_codo.moveTo(k*200)
    #     time.sleep(0.051)
    l_base.moveTo(k * ang,velo)
    i = i + 1
    for k in range(40):
        v = int(l_base.getSpeed())
#         print(get_now_format('%M:%S.%f'), v)
        #         no=now()
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

home(di)

# # Creamos un patrón, es decir un movimiento compuesto

pat = pattern(di)
pat.add('base', 0, -400, 100)
pat.add('codo', 0.5, -400, 10)
pat.add('codo', 2.9, -600, 100)
pat.get_df()

pat.run()

pat.run_rep(3)

home(di)

# # 9. Liberar el puerto

lss.closeBus()
