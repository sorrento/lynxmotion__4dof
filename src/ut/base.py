import time
from datetime import datetime
import numpy as np

FORMAT_DATE = "%Y%m%d"
FORMAT_DATETIME = '%Y-%m-%d %H:%M:%S.%f'
FORMAT_UTC = '%Y-%m-%dT%H:%M:%S.%fZ'
FORMAT_UTC2 = '%Y-%m-%d %H:%M:%S.%f+00:00'


def make_folder(path):
    import os
    try:
        if not os.path.isdir(path):
            print('Creando directorio ', path)
            os.mkdir(path)
        else:
            print('Ya existe: {}'.format(path))
    except OSError:
        print('Ha fallado la creación de la carpeta %s' % path)


def inicia(texto):
    ahora = time.time()
    print('** Iniciando: {}'.format(texto))

    return [ahora, texto]


def tardado(lista: list):
    start = lista[0]
    texto = lista[1]
    elapsed = (time.time() - start)
    strftime = time.strftime('%H:%M:%S', time.gmtime(elapsed))
    print('** Finalizado {}.  Ha tardado {}'.format(texto, strftime))
    return elapsed


def save_json(dic, path, datos_desc=''):
    """

    :param dic:
    :param path:
    :param datos_desc: sólo para mostrar en un print
    """
    import json
    path2 = path + '.json'
    print('** Guardado los datos ' + datos_desc + ' en {}'.format(path2))
    with open(path2, 'w', encoding="utf-8") as outfile:
        json.dump(dic, outfile, ensure_ascii=False)


def read_json(json_file):
    import json
    with open(json_file, encoding="utf-8") as in_file:
        data = json.load(in_file)
    return data


def get_now(utc=False):
    ct = now(utc)
    # ts = ct.timestamp()
    # print("timestamp:-", ts)

    return str(ct)  # podríamos quedarnos con el objeton (sin str)


def now(utc=False):
    from datetime import timezone, datetime
    if utc:
        tz = timezone.utc
    else:
        tz = None

    return datetime.now(tz)


def get_now_format(f=FORMAT_DATE, utc=False):
    """

    :param utc:
    :param f: ver https://pythonexamples.org/python-datetime-format/
    :return:
    """
    ct = now(utc)
    return ct.strftime(f)


def flatten(lista):
    """
transforma una lista anidada en una lista de componenetes únicos oredenados
    :param lista:
    :return:
    """
    from itertools import chain

    # los que no están en anidados los metemos en lista, sino no funciona la iteración
    lista = [[x] if (type(x) != list) else x for x in lista]
    flat_list = list(chain(*lista))

    return sorted(list(set(flat_list)))


def log10p(x):
    """
    equivalente a log1p pero en base 10, que tiene más sentido en dinero
    :param x:
    :return:
    """
    import numpy as np
    return np.log10(x + 1)


def abslog(x):
    """
    función logaritmica que incluye el 0, es espejo en negativos, y es "aproximadamente" base 10
    :param x:
    :return:
    """
    if x < 0:
        y = -log10p(-x)
    else:
        y = log10p(x)
    return y


def save_df(df, path, name, save_index=False, append_size=True):
    if append_size:
        middle = '_' + str(round(df.shape[0] / 1000)) + 'k_' + str(df.shape[1])
    else:
        middle = ''

    filename = path + '/' + name + middle + '.csv'
    print('** Guardando dataset en {}'.format(filename))
    df.to_csv(filename, index=save_index)

    return filename


def time_from_str(s, formato):
    return datetime.strptime(s, formato)


def time_to_str(t, formato):
    return t.strftime(formato)


def seq_len(ini, n, step):
    """
crea una secuencia de n enteros, a distancia step
    :param n:
    :param step:
    :param ini:
    :return:
    """
    end = ini + step * (n + 1)
    return list(np.arange(ini, end, step)[:n])


def nearest(x, lista):
    """
devuelve el número más cercano a x de la lista
    :param x:
    :param lista:
    :return:
    """
    deltas = [abs(s - x) for s in lista]
    pos = list_min_pos(deltas)

    return lista[pos]


def list_min_pos(lista):
    """
da la (primera) posición del elemento más pequeño
    :param lista:
    :return:
    """
    mi = min(lista)
    return lista.index(mi)


def json_from_string(s):
    import json
    return json.loads(s.replace("'", "\""))
