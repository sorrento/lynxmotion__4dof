import time
import pandas as pd

from u_base import now


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
    time.sleep(2)  # para garantizar que se detiene
    update_position(di)


def reset(di):
    print('***+CUIDADO que el brazo se CAERÁ')
    time.sleep(2)
    for k in di:
        di[k]['o'].reset()


class pattern:
    def __init__(self, di):
        self.moves = {}
        self.di = di

    def add(self, part, start, pos, vel):
        lista = ['base', 'hombro', 'codo', 'muneca', 'mano']
        if part in lista:
            aa = {start: {'o': part, 'pos': pos, 'vel': vel}}
            self.moves.update(aa)
        else:
            print('part debe ser uno de estos {}')

    def get_dic(self):
        return self.moves

    def get_df(self):
        df_move = pd.DataFrame.from_dict(self.moves, orient='index').reset_index().sort_values('index')
        df_move = df_move.rename(columns={'index': 'time'})

        return df_move

    def run(self, go_home=True):
        if go_home:
            home(self.di)

        delta = 0
        df = self.get_df()
        for i in range(len(df)):
            row = df.iloc[i, :]

            # wait sleeping
            if i > 0:
                r_prev = df.iloc[i - 1, :]
                delta = float(row['time']) - float(r_prev['time'])
            if delta > 0:
                time.sleep(delta)
                print('>>>Waiting ', delta)

            # move
            o = self.di[row.o]['o']
            o.moveTo(row.pos, row.vel)

            print('\n********** {} | {} (->{} vel:{}) | {}'.format(i, row.o, row.pos, row.vel, now()))

    def run_rep(self, n):
        for i in range(n):
            print('\n\n >>>>>>>>>>repeticion: {}/{}'.format(i + 1, n))
            self.run()


def get_variables(di):
    status = pd.DataFrame()
    for k in di:
        df, j = get_status(di[k]['o'], k, False)
        status = pd.concat([status, df])
        di[k]['status'] = j[k]

    return status


def plot_time(vels, title):
    import matplotlib.pyplot as plt

    # plt.style.use("fivethirtyeight")
    plt.figure(figsize=(12, 10))

    plt.xlabel("tick")
    plt.ylabel("Speed")
    plt.title(title)

    plt.plot(vels.t, vels["vel"], lw=1)
    # plt.plot(vels.time, vels["vel"])
