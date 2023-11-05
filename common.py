import pathlib


#SUBARU_PATH = pathlib.Path("C:\\Program Files (x86)\\subaru")
SUBARU_PATH = pathlib.Path("/mnt/c/Program Files (x86)/subaru")

DB_PATH = SUBARU_PATH / "SSM4" / "SUBARU" / "NA" / "DB"
FW_PATH = SUBARU_PATH / "FlashWrite"
ECU_DATA_PATH = FW_PATH / "EcuData"

OUTPUT_PATH = pathlib.Path(__file__).parent / "output"