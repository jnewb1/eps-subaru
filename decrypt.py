import pathlib
import struct
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

BASEDIR = pathlib.Path(__file__).parent

# Key computation
HASH = b'\xd4\xde\xe8\xdb\xcc\xdb\xd9\x92\x48\xb6\x9d\x88\xab\xae\xc0\x73\xbb\x8c\x84\x6f\x72\x7e\xb3\xc6\x8d\x74\xbc\xb4\xb7\xce\xe2\xe2\xff\x24\x1b\xbb\xe1\x32\x2f\x18'
h = SHA256.new()
h.update(HASH)
KEY = h.digest()

IV = b'\xa8\xb0\xc8\xc9\x6f\x9b\xaf\xb8\xbe\xc2\xc2\xa0\x89\x85\xb4\x8c'

aes = AES.new(KEY, AES.MODE_CBC, IV)

FW_FILENAME = BASEDIR / "82002FJ001_US.pak"

OUTPUT_DIR = BASEDIR / FW_FILENAME.stem

OUTPUT_DIR.mkdir(exist_ok=True)

FW_FP = BASEDIR / FW_FILENAME

HEADER_FILENAME = "header.csv"

KEYWORD = "B601692E"

def read_length(f, size=2):
    length = f.read(size)
    return struct.unpack('<H' if size == 2 else "<B", length)[0]

def read_string(f, size=2):
    length = read_length(f, size=size)
    return f.read(length).decode("UTF-8")

def read_opcode(f):
    opcode = f.read(2)
    return struct.unpack('<H', opcode)[0]

def read_section_body(filename, f):
    length = read_length(f)
    print(f"Reading {filename} with length {length}")

    return f.read(length)

def read_section(f):
    file_name = read_string(f, size=1)
    header = f.read(4)

    section = read_section_body(file_name, f)

    return section

def decrypt_file(fw_file):
    sections = []

    with open(fw_file, "rb") as f:
        header = f.read(4)

        sections.append(read_section_body(HEADER_FILENAME, f))

        unknown = f.read(2)

        while True:
            opcode = read_opcode(f)
            print(f"opcode: {opcode}")

            if opcode == 0x8001:
                pass
            elif opcode == 0xFFFF:
                unused = f.read(2)
                string = read_string(f)
                print(f"class: {string}")
            elif opcode == 0x0000:
                print("EOF")
                break

            sections.append(read_section(f))
    
    print(sections)

decrypt_file(FW_FP)