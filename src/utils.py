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