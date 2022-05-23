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

import lss
import lss_const as lssc
import time

CST_LSS_Port = "COM5"  # For windows platforms
CST_LSS_Baud = lssc.LSS_DefaultBaud

# +
lss.initBus(CST_LSS_Port, CST_LSS_Baud)

l_base = lss.LSS(1)
l_hombro_ = lss.LSS(2)
l_codo = lss.LSS(3)
l_muneca = lss.LSS(4)
l_mano = lss.LSS(5)


def get_status(myLSS):
    # Get the values from LSS
    print("\r\nQuerying LSS...")
    pos = myLSS.getPosition()
    rpm = myLSS.getSpeedRPM()
    curr = myLSS.getCurrent()
    volt = myLSS.getVoltage()
    temp = myLSS.getTemperature()
    # Display the values in terminal
    print("\r\n---- Telemetry ----")
    print("Position  (1/10 deg) = " + str(pos))
    print("Speed          (rpm) = " + str(rpm))
    print("Curent          (mA) = " + str(curr))
    print("Voltage         (mV) = " + str(volt))
    print("Temperature (1/10 C) = " + str(temp))


while 1:
    get_status(myLSS)
    time.sleep(1)

myLSS.getColorLED()

myLSS.move(0)

myLSS.move(-1800)
myLSS.move(1800)

l_codo.move(-100)

l_muneca.move(100)

l_hombro = lss.LSS(2)

l_hombro.move(300)

l_codo.setColorLED(2)

l_hombro.setColorLED(1)

l_codo.move(-300)
l_hombro.move(-300)

l_codo.move(-300)

l_mano.move(-300)
