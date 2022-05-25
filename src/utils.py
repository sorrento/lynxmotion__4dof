import random
import time
import pandas as pd
from IPython.core.display import display

import lss
import lss_const

from u_base import now, save_json, read_json, save_df


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

    print('Position (angles):', pose)


def home(di):
    for k in di:
        di[k]['o'].moveTo(0)
    time.sleep(1.5)  # para garantizar que se detiene
    update_position(di)


def reset(di):
    print('***+CUIDADO que el brazo se CAERÁ')
    time.sleep(2)
    for k in di:
        di[k]['o'].reset()


class Pattern:
    def __init__(self, di, name='name'):
        self.moves = {}
        self.di = di
        self.name = name

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

    def _run(self, start_home=True):
        if start_home:
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

    def run(self, n=1, end_home=True):
        for i in range(n):
            print('\n\n >>>>>>>>>>repeticion: {}/{}'.format(i + 1, n))
            self._run()
        if end_home:
            home(self.di)

    def create_random(self, n_moves=4, t_max=4):
        """
creación de movimientos random
        :param n_moves:
        :param t_max:
        """
        import random
        di = self.di
        partes = random.choices(list(di.keys()), k=n_moves)
        move = {}

        for k in partes:
            pos = random.randint(di[k]['min'], di[k]['max'])
            vel = random.randint(30, 300)
            d = {round(random.random() * t_max, 2): {'o': k, 'pos': pos, 'vel': vel}}
            move.update(d)

        self.moves = move
        display(self.get_df())

    def save(self):
        save_json(self.moves, 'data/move_' + self.name)

    def load(self, path):
        self.name = path.split('/')[-1].split('.')[0].split('_')[-1]
        print('Movimiento llamado: {}'.format(self.name))
        self.moves = read_json(path)
        display(self.get_df())


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


def init(CST_LSS_Port="COM5"):
    # Use the app LSS Flowarm that makes automatic scanning
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

    # fijamos los límites de movimiento
    for k in di:
        di[k]['min'] = -900
        di[k]['max'] = 900

    di['mano']['max'] = 0
    di['base']['min'] = -1800
    di['base']['max'] = 1800

    home(di)
    return di, l_base, l_hombro, l_codo, l_muneca, l_mano


def pat_from_file(di, file):
    a = Pattern(di)
    a.load(file)
    return a


class Experimento:
    def __init__(self, di, n, *files):
        moves = [pat_from_file(di, file) for file in files]
        self.r_moves = random.choices(moves, k=n)
        seq = [x.name for x in self.r_moves]
        print(seq)
        self.df = pd.DataFrame()

    def run(self):
        for m in self.r_moves:
            print(now(), ' doing ', m.name)
            df2 = pd.DataFrame({'time': [now()], 'move': [m.name]})
            self.df = pd.concat([self.df, df2])

            m.run()

    def save(self, name):
        save_df(self.df, 'data/', 'exp_' + name, append_size=False)
