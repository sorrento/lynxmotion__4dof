import os


def getmtime(filename):
    """Return the last modification time of a file, reported by os.stat()."""
    return os.stat(filename).st_mtime


def getatime(filename):
    """Return the last access time of a file, reported by os.stat()."""
    return os.stat(filename).st_atime


def getctime(filename):
    """Return the metadata change time of a file, reported by os.stat()."""
    return os.stat(filename).st_ctime


def lista_files_recursiva(path, ext, with_path=True, drop_extension=False, recursiv=True):
    """
devuelve la lista de archivos en la ruta, recursivamente, de la extensión especificada. la lista está ordenada por fecha
de modificación
    :param drop_extension:
    :param with_path:
    :param path:
    :param ext:
    :return:
    """
    import glob

    if recursiv:
        lista = glob.glob(path + '**/*.' + ext, recursive=recursiv)
    else:
        lista = glob.glob(path + '/*.' + ext, recursive=recursiv)

    lista = sorted(lista, key=getmtime, reverse=True)

    if not with_path:
        lista = [get_filename(x) for x in lista]

    if drop_extension:
        lista = [remove_extension(x) for x in lista]

    return lista


def remove_extension(filename):
    return '.'.join(filename.split('.')[:-1])


def fecha_mod(file):
    """
entrega la fecha de modificación de un archivo como un número yyyymmdd
    :param file:
    :return:
    """
    import datetime
    dt = datetime.datetime.fromtimestamp(getmtime(file))
    return int(dt.strftime('%Y%m%d'))


def get_filename(path, remove_ext=False):
    """
obtiene el nombre del fichero desde el path completo
    :param remove_ext: quitar la extension
    :param path:
    :return:
    """
    file = os.path.basename(path)
    if remove_ext:
        file = remove_extension(file)
    return file


def escribe_txt(txt, file_path):
    text_file = open(file_path, "wt")
    n = text_file.write(txt)
    text_file.close()


def lee_txt(file_path):
    """
lee fichero de texto
    :param file_path:
    :return:
    """
    import os
    if os.path.isfile(file_path):
        # open text file in read mode
        text_file = open(file_path, "r", encoding='utf-8')

        # read whole file to a string
        data = text_file.read()

        # close file
        text_file.close()
        return data
