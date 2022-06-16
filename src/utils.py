from datetime import timedelta, datetime
import pandas as pd
from influxdb_client import InfluxDBClient
from matplotlib import pyplot as plt

from config import TOKEN, ORG
from ut.base import time_from_str, FORMAT_UTC2, FORMAT_UTC, save_df
from ut.io import lista_files_recursiva, get_filename
from ut.timeSeries import to_ticked_time, get_tick


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


def prepare_one(j, dt, df, verbose=True):
    row = df.loc[j]
    t0 = row.time
    t1 = row.time_end
    if verbose:
        print('Movimiento j:{}, entre tiempos {} | {}'.format(j, t0, t1))
    b = dt[(dt.time >= t0) & (dt.time < t1)].copy()
    b['pat'] = row.pat
    b['i'] = j
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


def crea_dataset(dt, df, verbose=False):
    # l = False  # ponerlo en false si ya escribimos el fichero de movimientos con hora utc
    # limits = [ut(datetime.strptime(t, FORMAT_UTC2), local=l) for t in df.time]
    # limits.append(limits[-1] + timedelta(seconds=5))
    # limits_str = [t.strftime(FORMAT_UTC2) for t in limits]

    tot = pd.DataFrame()
    for j in df.index:
        b = prepare_one(j, dt, df, verbose)
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


def lee_influx(t0, t1):
    client = InfluxDBClient(url="http://localhost:8086", token=TOKEN, org=ORG)
    query_api = client.query_api()

    # Pedimos los datos correspondientes a la ventana temporal
    q = make_query(t0.strftime(FORMAT_UTC), t1.strftime(FORMAT_UTC))
    dataframe = query_api.query_data_frame(q)
    dt = dataframe[['_field', '_value', '_time']].rename(
        columns={'_field': 'variable', '_time': 'time', '_value': 'value'})

    return dt


def procesa_all(verbose=False):
    """
genera un dataset para cada fichero en data_med y los almacena
    :param verbose:
    """
    names = lista_files_recursiva('data_med/Experimentos/', 'json',
                                  with_path=False, drop_extension=True, recursiv=False)
    names = [x.replace('_real', '') for x in names]
    for name in names:
        process_one(name, verbose)


def process_one(base, verbose=False):
    print('\n*************** PROCESANDO:', base)

    # 1 Dataset de mov del BRAZO
    csv = 'data_med/Experimentos/' + base + '.csv'
    df = pd.read_csv(csv)
    df['time_end'] = df.time.shift(-1)
    df = df[df.pat != 'GH'].set_index('i')

    # 2 Dataset de series temporales del SENSOR
    import os
    path_time = 'data_med/Experimentos/time/' + base + '.csv'
    existe = os.path.exists(path_time)
    if not existe:
        t0 = datetime.strptime(df.time.iloc[0], FORMAT_UTC2)
        t1 = datetime.strptime(df.time.iloc[-1], FORMAT_UTC2)
        t1 = t1 + timedelta(seconds=2)  # sumamos 2 para captar el último movimiento

        dt = lee_influx(t0, t1)
        path_time = save_df(dt, 'data_med/Experimentos/time', base, append_size=False)
    dt = pd.read_csv(path_time)

    # 3 Combianación de ambos datasets
    tot = crea_dataset(dt, df, verbose)

    # agregamos la variable tt con tiempos en ticks
    times = [time_from_str(x, FORMAT_UTC2) for x in dt.time.unique()]
    tic = get_tick(times, plotea=False, verbose=False)

    if tic != 90:
        print('tic no es 90: ', tic)
        if abs(tic - 90) > 5:
            print('**ES Grave en ', base)
            tic = get_tick(times, plotea=True)
            tic = None
        else:
            tic = 90

    tot['tt'] = tot['t'].map(
        lambda x: to_ticked_time(x, tic))  # todo: es posible que haya agujeros (ticks sin valor en alguna var)

    save_df(tot, path='data_out', name=base, append_size=False)


def une_datasets():
    def procesa(file):
        df = pd.read_csv(file)
        df = df.drop(columns=['t', 'time'])
        df['exp'] = get_filename(file, remove_ext=True)
        return df

    files = lista_files_recursiva('data_out/', 'csv', recursiv=False)
    df_all = pd.concat([procesa(x) for x in files]).reset_index(drop=True)

    save_df(df_all, 'data_out/all', 'all', append_size=False)
    return df_all