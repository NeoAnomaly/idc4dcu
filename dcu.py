from dcu_defs import *
import dcu_reader

class _ExceptionHelper:
    def throw_not_supported_version(magic):
        raise ValueError("Not supported version. magic: 0x%X" % magic)

    def throw_format_error(self, message):
        raise ValueError(message)


class DelphiCompiledUnit:
    def __init__(self):
        self.reader = None
        self.version = 0
        self.flags = 0
        self.source_files = []
        
    def _parse_magic(self, magic):
        if magic in DelphiCompiledUnitVersions.MAGIC_TO_VERSION:
            self.version = DelphiCompiledUnitVersions.MAGIC_TO_VERSION[magic]
        elif magic & 0x00FF00F9 == 0x00000049:
            version = magic >> 24

            if 0x1f < version < 0x17:
                _ExceptionHelper.throw_not_supported_version(magic)

            self.version = version + (DelphiCompiledUnitVersions.DCU_VERSION_D_XE2 - 0x17)
        else:
            _ExceptionHelper.throw_not_supported_version(magic)

        print("Dcu MagicNumber: 0x%x version: %d" % (magic, self.version))
        
    def _read_header(self):
        magic_number = self.reader.read_u32()
        self._parse_magic(magic_number)

        fileSize = self.reader.read_u32()
        fileTime = self.reader.read_u32()

        if self.version == DelphiCompiledUnitVersions.DCU_VERSION_D2:
            self.reader.advance(1)  # Unknown byte
            # chunk_id = self.reader.read_u8()
        else:
            stamp = self.reader.read_u32()
            self.reader.advance(1)  # Unknown byte

            if self.version >= DelphiCompiledUnitVersions.DCU_VERSION_D7:
                self.reader.advance(1)  # Another unknown byte

            if self.version >= DelphiCompiledUnitVersions.DCU_VERSION_D2005:
                name = self.reader.read_string()
                print('Dcu name: ', name)

            if self.version >= DelphiCompiledUnitVersions.DCU_VERSION_D2009:
                self.reader.read_u_index(self.version)
                self.reader.read_u_index(self.version)

            chunk_id = self.reader.read_u8()
            if chunk_id == DelphiCompiledUnitChunks.UNIT_FLAGS:
                self.flags = self.reader.read_u_index(self.version)[0]

                if self.version > DelphiCompiledUnitVersions.DCU_VERSION_D2005:
                    flags1 = self.reader.read_u_index(self.version)

                if self.version > DelphiCompiledUnitVersions.DCU_VERSION_D3:
                    unit_prior = self.reader.read_u_index(self.version)

                #chunk_id = self.reader.read_u8()
            else:
                # Unit flags chunk not found, revert reader position
                self.reader.advance(-1)

        print('Header read complete. Flags: 0x%x' % (self.flags))

    def _read_source_files(self):
        chunk_id = self.reader.read_u8()

        print('Source files:')
        while (chunk_id == DelphiCompiledUnitChunks.SRC
               or
               chunk_id == DelphiCompiledUnitChunks.RESOURCE
               or
               chunk_id == DelphiCompiledUnitChunks.OBJ
               or
               chunk_id == DelphiCompiledUnitChunks.ASM
               or
               chunk_id == DelphiCompiledUnitChunks.INLINE_SRC):

            name = self.reader.read_name(self.version)
            self.source_files.append(name)
            print('\t', name)

            self.reader.read_u32()
            self.reader.read_u_index(self.version)

            chunk_id = self.reader.read_u8()

        if not self.source_files:
            _ExceptionHelper.throw_format_error('Source files not found')


    def load(self, filepath):
        print('Start loading: ', filepath)

        self.reader = dcu_reader.DelphiCompiledUnitReader(filepath)

        self._read_header()
        self._read_source_files()
        ord('v')


if __name__ == "__main__":
    dcu = DelphiCompiledUnit()
    dcu.load('xe7.dcu')

    print('')

    dcu.load('d7.dcu')
