import io
import struct

class open_ext:
    def __init__ (self, *args):
        self.file = open(*args)

    def __getattr__(self, attr):
        return getattr(self.file, attr)

    def __enter__ (self):
        return self

    def __exit__ (self, exc_type, exc_value, traceback):
        self.file.close()

    def skip(self, bytes):
        self.file.seek(bytes, io.SEEK_CUR)

    def read_until_zero(self):
        out = b''
        byte = self.file.read(1)
        while byte != b"\x00":
            out += byte
            byte = self.file.read(1)
        return out

    def read_u32_le(self):
        return struct.unpack('<I', self.file.read(4))[0]

    def write_u32_le(self, x):
        self.file.write(struct.pack('<I', x))
