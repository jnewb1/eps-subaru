import os
import pathlib
import struct
from Crypto.Cipher import ARC2
from common import FW_PATH, OUTPUT_PATH

BASEDIR = pathlib.Path(__file__).parent


class SubaruFWFile:
    HEADER_FILENAME = "header.csv"
    
    def __init__(self, filename: pathlib.Path, keyword: str):
        self.arc = ARC2.new(keyword.encode("utf-8"), ARC2.MODE_CBC)
    
        self.keyword = keyword
        self.f = open(filename, "rb")

        self.f.seek(0, os.SEEK_END)
        file_size = self.f.tell()
        self.f.seek(0)

        self.sections = {}
        header = self.f.read(4)

        self.sections[self.HEADER_FILENAME] = self.read_section_body(self.HEADER_FILENAME)

        unknown = self.f.read(2)

        while True:
            opcode = self.read_opcode()
            print(f"opcode: {opcode}")

            if opcode == 0x8001:
                pass
            elif opcode == 0xFFFF:
                unused = self.f.read(2)
                string = self.read_string()
                print(f"class: {string}")
            elif opcode == 0x0000:
                print("EOF")
                break

            self.read_section()

            if self.f.tell() == file_size:
                print("EOF2")
                break

        self.decrypt_sections()
    
    def decrypt_sections(self):
        for filename in self.sections.keys():
            self.sections[filename] = self.arc.decrypt(self.sections[filename])

    def read_length(self, size=2):
        length = self.f.read(size)
        length = struct.unpack('<H' if size == 2 else "<B", length)[0]

        if length == 0xFFFF:
            length = self.f.read(4)
            length = struct.unpack('<I', length)[0]
        
        return length


    def read_string(self, size=2):
        length = self.read_length(size=size)
        print(length)
        d = self.f.read(length)
        print(d)
        return d.decode("UTF-8")

    def read_opcode(self):
        opcode = self.f.read(2)
        return struct.unpack('<H', opcode)[0]

    def read_section_body(self, filename):
        length = self.read_length()
        print(f"Reading {filename} with length {length}")

        return self.f.read(length)

    def read_section(self):
        file_name = self.read_string(size=1)
        header = self.f.read(4)

        self.sections[file_name] = self.read_section_body(file_name)

    def save_sections(self, output_dir: pathlib.Path):
        output_dir.mkdir(parents=True, exist_ok=True)

        for filename in self.sections.keys():
            with open(output_dir / filename, "wb") as f:
                f.write(self.sections[filename])
        
fw = SubaruFWFile(FW_PATH / "82002FJ001_US.pak", "B601692E")
fw.save_sections(OUTPUT_PATH / "FW" / "82002FJ001_US")