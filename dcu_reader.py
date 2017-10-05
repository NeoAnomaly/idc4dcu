import sys
from binaryreader import BinaryReader
from dcu_defs import *

class DelphiCompiledUnitReader(BinaryReader):
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

                        if (version > DelphiCompiledUnitVersions.DCU_VERSION_D3
                            and
                            index_bytes[0] & 0xF0 != 0):
                            ndx = self.read_u32()

                        return (int.from_bytes(index_bytes, sys.byteorder), ndx)


    def read_index(self):
        pass

    def read_name(self, version):
        length = self.read_u8()

        if length == 0xFF and version >= DelphiCompiledUnitVersions.DCU_VERSION_D2009:
            length = self.read_u32()

        return self.read_raw(length).decode('ascii')
