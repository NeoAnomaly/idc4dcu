import io
import struct


class BinaryReader:
    type_names = {
        'int8':   'b',
        'uint8':  'B',
        'int16':  'h',
        'uint16': 'H',
        'int32':  'i',
        'uint32': 'I',
        'int64':  'q',
        'uint64': 'Q',
        'float':  'f',
        'double': 'd',
        'char':   's'
    }

    def __init__(self, filepath, encoding="ascii"):
        self._file = open(filepath, 'rb')
        self._encoding = encoding

    def __del__(self):
        self._file.close()

    def _read(self, typename):
        typeformat = BinaryReader.type_names[typename.lower()]
        typesize = struct.calcsize(typeformat)

        value = self._file.read(typesize)

        if len(value) != typesize:
            raise IOError

        return struct.unpack(typeformat, value)[0]

    def advance(self, count):
        self._file.seek(count, io.SEEK_CUR)

    def tell(self):
        return self._file.tell()

    def read_s8(self):
        return self._read('int8')

    def read_u8(self):
        return self._read('uint8')

    def read_s32(self):
        return self._read('int32')

    def read_u32(self):
        return self._read('uint32')

    def read_string(self):
        length = self.read_u8()
        return self._file.read(length).decode(self._encoding)