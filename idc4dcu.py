import sys
from binaryreader import BinaryReader


def read_dcu_header(filepath):
    reader = BinaryReader(filepath)
    magic = reader.read_u32()
    print('0x%x' % magic, type(magic))


def print_path():
    for path in sorted(sys.path):
        print(path)


def print_namespace(module, verbose=True):
    seplen = 60
    sepchr = '-'
    sepline = sepchr * seplen
    if verbose:
        print(sepline)
        print('name:', module.__name__, 'file:', 'None' if not hasattr(module, __file__) else module.__file__)
        print(sepline)

    count = 0
    for attr in module.__dict__:  # Сканировать пространство имен
        print("%02d) %s" % (count, attr), end='')
        if attr.startswith('__'):
            print("<built-in name>")  # Пропустить __file__ и др.
        else:
            print(getattr(module, attr))  # То же, что и .__dict__[attr]

        count = count + 1

    if verbose:
        print(sepline)
        print(module.__name__, "has %d names" % count)
        print(sepline)


if __name__ == "__main__":
    read_dcu_header("dcu32.dcu")
    """
    print("From main")
    print_path()
    import time
    print_namespace(time)
    """
