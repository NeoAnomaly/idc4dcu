from binaryreader import BinaryReader
import sys

class _DelphiCompiledUnitChunks:
    UNIT_FLAGS = 0x96

class _DelphiCompiledUnitVersions:
    DCU_VERSION_D2 = 2
    DCU_VERSION_D4 = 4
    DCU_VERSION_D3 = 3
    DCU_VERSION_D5 = 5
    DCU_VERSION_D6 = 6
    DCU_VERSION_D7 = 7
    DCU_VERSION_D8 = 8
    DCU_VERSION_D2005 = 9
    DCU_VERSION_D2006 = 10
    DCU_VERSION_D2009 = 12
    DCU_VERSION_D2010 = 14
    DCU_VERSION_D_XE = 15
    DCU_VERSION_D_XE2 = 16
    DCU_VERSION_D_XE3 = 17
    DCU_VERSION_D_XE4 = 18
    DCU_VERSION_D_XE5 = 19
    DCU_VERSION_D_XE6 = 20
    DCU_VERSION_D_XE7 = 21
    DCU_VERSION_D_XE8 = 22
    DCU_VERSION_D_10 = 23
    DCU_VERSION_D_10_1 = 24

    MAGIC_TO_VERSION = {
        0x50505348: DCU_VERSION_D2,
        0x44518641: DCU_VERSION_D3,
        0x4768A6D8: DCU_VERSION_D4,
        0xF21F148B: DCU_VERSION_D5,

        0x0E0000DD: DCU_VERSION_D6,
        0x0E8000DD: DCU_VERSION_D6,

        0xFF0000DF: DCU_VERSION_D7,
        0x0F0000DF: DCU_VERSION_D7,
        0x0F8000DF: DCU_VERSION_D7,

        0x10000229: DCU_VERSION_D8,

        0x11000239: DCU_VERSION_D2005,
        0x1100000D: DCU_VERSION_D2005,
        0x11800009: DCU_VERSION_D2005,

        0x1200024D: DCU_VERSION_D2006,
        0x12000023: DCU_VERSION_D2006,

        0x14000039: DCU_VERSION_D2009,
        0x15000045: DCU_VERSION_D2010,
        0x1600034B: DCU_VERSION_D_XE
    }

class _DelphiCompiledUnitReader(BinaryReader):
    def read_u_index(self, version):
        """"
        Returns (index, ndx hi dword)
        """
        index_bytes = []

        index_bytes.append(self.read_u8())
        if index_bytes[0] & 0x1 == 0:
            return (int.from_bytes(index_bytes, sys.byteorder) >> 1, 0)
        else:
            index_bytes.append(self.read_u8())
            if index_bytes[0] & 0x2 == 0:
                return (int.from_bytes(index_bytes, sys.byteorder) >> 2, 0)
            else:
                index_bytes.append(self.read_u8())
                index_bytes.append(0)
                if index_bytes[0] & 0x4 == 0:
                    return (int.from_bytes(index_bytes, sys.byteorder) >> 3, 0)
                else:
                    index_bytes[3] = self.read_u8()
                    if index_bytes[0] & 0x8 == 0:
                        return (int.from_bytes(index_bytes, sys.byteorder) >> 4, 0)
                    else:
                        index_bytes.append(self.read_u8())
                        ndx = 0

                        if (version > _DelphiCompiledUnitVersions.DCU_VERSION_D3
                            and
                            index_bytes[0] & 0xF0 != 0):
                            ndx = self.read_u32()

                        return (int.from_bytes(index_bytes, sys.byteorder), ndx)


    def read_index(self):
        pass

class _DelphiCompiledUnitHeader:

    def __init__(self):
        self.version = 0
        self.flags = 0

    def _throw_not_supported_version(self, magic):
        raise ValueError("Not supported version. magic: 0x%X" % magic)

    def _parse_magic(self, magic):
        if magic in _DelphiCompiledUnitVersions.MAGIC_TO_VERSION:
            self.version = _DelphiCompiledUnitVersions.MAGIC_TO_VERSION[magic]
        elif magic & 0x00FF00F9 == 0x00000049:
            version = magic >> 24

            if 0x1f < version < 0x17:
                self._throw_not_supported_version(magic)

            self.version = version + (_DelphiCompiledUnitVersions.DCU_VERSION_D_XE2 - 0x17)
        else:
            self._throw_not_supported_version(magic)

        print("Dcu MagicNumber: 0x%x version: %d" % (magic, self.version))

    def read(self, reader):
        magic_number = reader.read_u32()
        self._parse_magic(magic_number)

        fileSize = reader.read_u32()
        fileTime = reader.read_u32()

        if self.version == _DelphiCompiledUnitVersions.DCU_VERSION_D2:
            reader.advance(1)   # Unknown byte
            tag = reader.read_u8()
        else:
            stamp = reader.read_u32()
            reader.advance(1)   # Unknown byte

            if self.version >= _DelphiCompiledUnitVersions.DCU_VERSION_D7:
                reader.advance(1)   # Another unknown byte

            if self.version >= _DelphiCompiledUnitVersions.DCU_VERSION_D2005:
                name = reader.read_string()
                print(name)

            if self.version >= _DelphiCompiledUnitVersions.DCU_VERSION_D2009:
                reader.read_u_index(self.version)
                reader.read_u_index(self.version)

            tag = reader.read_u8()
            if tag == _DelphiCompiledUnitChunks.UNIT_FLAGS:
                self.flags = reader.read_u_index(self.version)

                if self.version > _DelphiCompiledUnitVersions.DCU_VERSION_D2005:
                    flags1 = reader.read_u_index(self.version)

                if self.version > _DelphiCompiledUnitVersions.DCU_VERSION_D3:
                    unit_prior = reader.read_u_index(self.version)

                tag = reader.read_u8()

        print('Header read complete. Tag: 0x%x' % tag)

class DelphiCompiledUnit:
    def __init__(self):
        self.header = _DelphiCompiledUnitHeader()
        self.reader = None

    def load(self, filepath):
        print('Start loading: ', filepath)

        self.reader = _DelphiCompiledUnitReader(filepath)

        self.header.read(self.reader)


if __name__ == "__main__":
    dcu = DelphiCompiledUnit()
    dcu.load('xe7.dcu')

    print('')

    dcu.load('d7.dcu')
