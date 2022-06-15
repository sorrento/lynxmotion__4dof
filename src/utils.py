from datetime import timedelta, datetime
import pandas as pd
from matplotlib import pyplot as plt

from ut.base import time_from_str, FORMAT_UTC2, FORMAT_DATETIME


def plot_time(vels, title):
    import matplotlib.pyplot as plt

    # plt.style.use("fivethirtyeight")
    plt.figure(figsize=(12, 10))

    plt.xlabel("tick")
    plt.ylabel("Speed")
    plt.title(title)

    plt.plot(vels.t, vels["vel"], lw=1)
    # plt.plot(vels.time, vels["vel"])


def get_di_empty():
    return {'base':   {'o': 'l_base'},
            'hombro': {'o': 'l_hombro'},
            'codo':   {'o': 'l_codo'},
            'muneca': {'o': 'l_muneca'},
            'mano':   {'o': 'l_mano'},
            }


def make_query(t0, t1, average=False):
    """
Trae todos los campos para los tiempos UTC entre t0 y t1
    :param t0: tienen que estar en este formato (UTC) 2022-05-25T10:00:00Z
    :param t1:
    :param average: si se pone TRUE se promediará cada segundo
    :return:
    """
    q0 = """from(bucket: "samva")
 |> range(start: %s, stop: %s)
 |> filter(fn: (r) => r["_field"] == "f2" or r["_field"] == "f0" or r["_field"] == "f1" or r["_field"] == "a0" or r["_field"] == "a1" or r["_field"] == "a2" or r["_field"] == "g0" or r["_field"] == "g1" or r["_field"] == "g2" or r["_field"] == "c0" or r["_field"] == "c1" or r["_field"] == "c2") """ % (
        t0, t1)

    q1 = """|> aggregateWindow(every: 1s, fn: mean, createEmpty: false)
  |> yield(name: "mean")"""

    if average:
        q0 = q0 + q1

    print(q0)
    return q0


def plot_one_var(dt, var):
    import matplotlib.pyplot as plt

    f = dt[dt.variable == var]
    plt.figure(figsize=(12, 10))

    plt.xlabel("time(-2)")
    plt.ylabel("g?")
    plt.title(var)

    plt.plot(f.time, f.value, lw=1)


def prepare_one(j, dt, df, limits_str):
    i = j + 1
    t0, t1 = limits_str[j], limits_str[j + 1]
    print('Movimiento i:{}, entre tiempos {} | {}'.format(i, t0, t1))

    b = dt[(dt.time >= t0) & (dt.time < t1)].copy()
    b['i'] = i
    b['pat'] = df.loc[i].pat
    # columna de tiempo absoluto en ms
    t_ref = time_from_str(b.iloc[0].time, FORMAT_UTC2)
    b['t'] = b['time'].map(lambda x: round((time_from_str(x, FORMAT_UTC2) - t_ref).total_seconds() * 1000))

    return b


def ut(t, local=True):
    #     resta dos horas si está en  hora local, para quedar en utc
    # puede que falle en horario de verano o invierno
    if local:
        #         print(p)
        t0 = t + timedelta(hours=-2)
    else:
        t0 = t
    return t0


def crea_dataset(dt, df):
    l = False  # ponerlo en false si ya escribimos el fichero de movimientos con hora utc
    limits = [ut(datetime.strptime(t, FORMAT_UTC2), local=l) for t in df.time]
    limits.append(limits[-1] + timedelta(seconds=5))
    limits_str = [t.strftime(FORMAT_UTC2) for t in limits]

    tot = pd.DataFrame()
    for j in range(len(df)):
        b = prepare_one(j, dt, df, limits_str)
        tot = pd.concat([tot, b])

    return tot


def plot_one_move_var(tot, var, mov, fa=1):
    # var = 'a0'
    # mov = 'C'
    import matplotlib.pyplot as plt
    f = tot[(tot.pat == mov) & (tot.varible == var)]

    pi = pd.pivot(f, columns='i', values='value', index='t').reset_index()
    cols = pi.columns.to_list()[1:]

    plt.figure(figsize=(12 / fa, 10 / fa))

    plt.xlabel("time")
    plt.ylabel("g?")
    plt.title('Move: {}  var:{}'.format(mov, var))

    for co in cols:
        mask = ~ pi[co].isna()
        plt.plot(pi['t'][mask], pi[co][mask], label='Line ' + str(co), lw=1)


def plot_umaps(embedding, dfp_):
    plt.figure(figsize=(20, 20))
    for i, v in enumerate(['tt', 'class']):
        plt.subplot(2, 2, i + 1)
        plt.scatter(
            embedding[:, 0],
            embedding[:, 1],
            c=dfp_[v].values, s=1, alpha=1)
        plt.gca().set_aspect('equal', 'datalim')
        plt.title(v, fontsize=24)


