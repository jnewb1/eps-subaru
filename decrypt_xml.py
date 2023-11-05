from Crypto.Cipher import AES
import pathlib

from common import DB_PATH, OUTPUT_PATH

key = b'\x46\x6A\x41\xAA\x5C\xE0\xFA\xF8\xF0\x2F\x15\x48\xEC\xE2\xC2\xCD\x1B\x5B\x01\x84\xA9\x3F\xF7\x62\xBF\x14\x65\xF8\x10\xD4\x8C\x9E'
iv =  b'\xA8\xB0\xC8\xC9\x6F\x9B\xAF\xB8\xBE\xC2\xC2\xA0\x89\x85\xB4\x8C'

cipher = AES.new(key, AES.MODE_CBC, iv)

def decrypt_xml(db_path: pathlib.Path, output_path: pathlib.Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    open(output_path, "wb").write(cipher.decrypt(open(db_path, "rb").read()))

for file in DB_PATH.glob("*.xml"):
    decrypt_xml(file, OUTPUT_PATH / "DB" / file.name)