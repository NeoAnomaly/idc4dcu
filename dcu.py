from dcu_defs import DelphiCompiledUnitChunks as Chunks, DelphiCompiledUnitVersions as Versions
import dcu_reader


class _ExceptionHelper:
    @staticmethod
    def throw_not_supported_version(magic):
        raise ValueError("Not supported version. magic: 0x%X" % magic)

    @staticmethod
    def throw_format_error(message):
        raise ValueError(message)


class DelphiCompiledUnit:
    def __init__(self):
        self.reader: dcu_reader.DelphiCompiledUnitReader = None
        self.version = 0
        self.flags = 0
        self.source_files = []
        self.current_chunk_id = 0

    def _parse_magic(self, magic):
        if magic in Versions.MAGIC_TO_VERSION:
            self.version = Versions.MAGIC_TO_VERSION[magic]
        elif magic & 0x00FF00F9 == 0x00000049:
            version = magic >> 24

            if 0x1f < version < 0x17:
                _ExceptionHelper.throw_not_supported_version(magic)

            self.version = version + (Versions.DCU_VERSION_D_XE2 - 0x17)
        else:
            _ExceptionHelper.throw_not_supported_version(magic)

        print("Dcu MagicNumber: 0x%x version: %d" % (magic, self.version))

    def _read_header(self):
        magic_number = self.reader.read_u32()
        self._parse_magic(magic_number)

        fileSize = self.reader.read_u32()
        fileTime = self.reader.read_u32()

        if self.version == Versions.DCU_VERSION_D2:
            self.reader.advance(1)  # Unknown byte
            self.current_chunk_id = self.reader.read_u8()
        else:
            stamp = self.reader.read_u32()
            self.reader.advance(1)  # Unknown byte

            if self.version >= Versions.DCU_VERSION_D7:
                self.reader.advance(1)  # Another unknown byte

            if self.version >= Versions.DCU_VERSION_D2005:
                name = self.reader.read_string()
                print('Dcu name: ', name)

            if self.version >= Versions.DCU_VERSION_D2009:
                self.reader.read_u_index(self.version)
                self.reader.read_u_index(self.version)

            self.current_chunk_id = self.reader.read_u8()
            if self.current_chunk_id == Chunks.UNIT_FLAGS:
                self.flags = self.reader.read_u_index(self.version)[0]

                if self.version > Versions.DCU_VERSION_D2005:
                    flags1 = self.reader.read_u_index(self.version)

                if self.version > Versions.DCU_VERSION_D3:
                    unit_prior = self.reader.read_u_index(self.version)

                self.current_chunk_id = self.reader.read_u8()

        print('Header read complete. Flags: 0x%x' % (self.flags))

    def _read_source_files(self):
        print('Source files:')
        while (self.current_chunk_id == Chunks.SRC
                or
                self.current_chunk_id == Chunks.RESOURCE
                or
                self.current_chunk_id == Chunks.OBJ
                or
                self.current_chunk_id == Chunks.ASM
                or
                self.current_chunk_id == Chunks.INLINE_SRC):

            name = self.reader.read_name(self.version)
            self.source_files.append(name)
            print('\t', name)

            self.reader.read_u32()
            self.reader.read_u_index(self.version)

            self.current_chunk_id = self.reader.read_u8()

        if not self.source_files:
            _ExceptionHelper.throw_format_error('Source files not found')

    def _read_uses(self, start_chunk_id):

        import_display_names = {
            Chunks.INTERFACE_USES: 'Interface uses section',
            Chunks.IMPL_USES: 'Implementation uses section',
            Chunks.DLL: 'DLL import'
        }

        print(import_display_names[start_chunk_id])

        while self.current_chunk_id == start_chunk_id:
            name = self.reader.read_name(self.version)

            print('\timport from %s:' % name)

            if start_chunk_id != Chunks.DLL and self.version >= Versions.DCU_VERSION_D8:
                self.reader.read_u_index(self.version)

            if self.version >= Versions.DCU_VERSION_D2006:
                self.reader.read_u_index(self.version)
            else:
                self.reader.read_u32()

            if (self.version == Versions.DCU_VERSION_D7
                or
                (
                self.version >= Versions.DCU_VERSION_D8
                and
                start_chunk_id == Chunks.DLL)):
                self.reader.read_u32()

            if self.version >= Versions.DCU_VERSION_D2009:
                self.reader.read_u_index(self.version)

            while True:
                self.current_chunk_id = self.reader.read_u8()

                if (self.current_chunk_id in [Chunks.IMPORT_TYPE, Chunks.IMPORT_TYPE_DEF]):
                    if start_chunk_id != Chunks.DLL:
                        import_name = self.reader.read_name(self.version)

                        print('\t\ttype: %s' % import_name)

                        if self.current_chunk_id == Chunks.IMPORT_TYPE_DEF:
                            rtti = self.reader.read_u_index(self.version)

                        self.reader.read_u32()

                elif self.current_chunk_id == Chunks.IMPORT_VALUE:
                    import_name = self.reader.read_name(self.version)

                    print('\t\tvalue: %s' % import_name)

                    self.reader.read_u32()

                elif self.current_chunk_id == Chunks.STOP2:
                    if self.version >= Versions.DCU_VERSION_D8:
                        self.reader.read_u32()

                    continue

                elif self.current_chunk_id == Chunks.CONST_ADD_INFO:
                    break

                else:
                    break

            if self.current_chunk_id != Chunks.STOP:
                _ExceptionHelper.throw_format_error(
                    'Unexcepted chunk 0x%x at %d' % (self.current_chunk_id, self.reader.tell())
                )

            self.current_chunk_id = self.reader.read_u8()

            if self.current_chunk_id == Chunks.CONST_ADD_INFO:
                if self.version < Versions.DCU_VERSION_D7:
                    break

                self.reader.read_index(self.version)

                self.current_chunk_id = self.reader.read_u8()


    def _read_declarations(self):
        pass


    def load(self, filepath):
        print('Start loading: ', filepath)

        self.reader = dcu_reader.DelphiCompiledUnitReader(filepath)

        self._read_header()
        self._read_source_files()
        self._read_uses(Chunks.INTERFACE_USES)
        self._read_uses(Chunks.IMPL_USES)
        self._read_uses(Chunks.DLL)
        self._read_declarations()


if __name__ == "__main__":
    dcu = DelphiCompiledUnit()
    dcu.load('xe7.dcu')

    print('')

    dcu.load('d7.dcu')
