import csv
import itertools
import os
import pathlib
import struct
from Crypto.Cipher import ARC2
from Crypto.Hash import MD5
from common import ECU_DATA_PATH, FW_PATH, OUTPUT_PATH

BASEDIR = pathlib.Path(__file__).parent


def create_part_database():
    db = {}
    for csv_filename in FW_PATH.glob("*.csv"):
        with open(csv_filename, "r", encoding='utf-16') as f:
            reader = csv.DictReader(f)

            for row in reader:
                db[row["Part_Number"]] = row["Keyword"]
                db[row["Pack_Number"]] = row["Keyword"]
   
    return db

class SubaruFWFile:
    HEADER_FILENAME = "header.csv"

    PART_NO_TO_KEYWORD = create_part_database()
    
    def __init__(self, filename: pathlib.Path):
        part_no = filename.stem
        if part_no not in self.PART_NO_TO_KEYWORD:
            raise Exception(f"{part_no} not in pack db")

        self.keyword = self.PART_NO_TO_KEYWORD[filename.stem]
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
            if opcode == 0x8001:
                pass
            elif opcode == 0xFFFF:
                unused = self.f.read(2)
                string = self.read_string()
            elif opcode == 0x0000:
                break

            self.read_section()

            if self.f.tell() == file_size:
                break

        self.decrypt_sections()

    def decrypt_sections(self):
        RC2_SALT = b'\x00' * 11
        RC2_IV = b'\x00' * 8
        RC2_EFFECTIVE_KEYLEN = 40

        for filename in self.sections.keys():
            keyword = "CsvKey" if filename == "header.csv" else self.keyword
            h = MD5.new()
            h.update(keyword.encode("utf-8"))

            key = h.digest()[0:5] + RC2_SALT

            arc = ARC2.new(key, ARC2.MODE_CBC, iv=RC2_IV, effective_keylen=RC2_EFFECTIVE_KEYLEN)
            self.sections[filename] = arc.decrypt(self.sections[filename])

    def read_length(self, size=2):
        length = self.f.read(size)
        length = struct.unpack('<H' if size == 2 else "<B", length)[0]

        if length == 0xFFFF:
            length = self.f.read(4)
            length = struct.unpack('<I', length)[0]
        
        return length

    def read_string(self, size=2):
        length = self.read_length(size=size)
        d = self.f.read(length)
        return d.decode("UTF-8")

    def read_opcode(self):
        opcode = self.f.read(2)
        return struct.unpack('<H', opcode)[0]

    def read_section_body(self, filename):
        length = self.read_length()
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

for filename in itertools.chain(ECU_DATA_PATH.glob("*.pak"), ECU_DATA_PATH.glob("*.pk2")):
    fw = SubaruFWFile(filename)
    fw.save_sections(OUTPUT_PATH / "FW" / filename.stem)