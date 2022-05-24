import pandas as pd


def get_status(myLSS, name="Telemetry", imprime=True):
    pos = myLSS.getPosition()
    rpm = myLSS.getSpeedRPM()
    curr = myLSS.getCurrent()
    volt = myLSS.getVoltage()
    temp = myLSS.getTemperature()

    if imprime:
        print("\nQuerying LSS... ", name)
        print("\r\n---- %s ----" % name)
        print("Position  (1/10 deg) = " + str(pos))
        print("Speed          (rpm) = " + str(rpm))
        print("Curent          (mA) = " + str(curr))
        print("Voltage         (mV) = " + str(volt))
        print("Temperature (1/10 C) = " + str(temp))

    df = pd.DataFrame({'name': [name], 'pos': [pos], 'rpm': [rpm],
                       'curr': [curr], 'volt': [volt], 'temp': [temp]}).set_index('name')
    dic = df.to_dict(orient='index')

    return df, dic


def update_position(di):
    pose = []
    for k in di:
        #         print(k)
        o = di[k]['o']
        pos = int(o.getPosition())
        di[k]['pos'] = pos
        pose.append(pos)

    print(pose)


def home(di):
    for k in di:
        di[k]['o'].moveTo(0)
    update_position(di)
