# Subaru EPS firmware decrpytion and analysis

### pk2 decryption thanks to [atlas-tuning](https://github.com/atlas-tuning)!
https://github.com/atlas-tuning/utilities/blob/main/java/src/main/java/com/github/manevolent/atlas/ssm4/PakFile.java

## Getting Started
modify common.py to the path to your SSM4 installation

```bash
pip install -r requirements.txt
python decrypt_fw.py # decrypt example firmware
python decrypt_xml.py # decrypt xml

ls output/DB/ # XML data about how SSM4 operates and keys
ls output/FW/ # extracted versions of firmware
```

2021 outback EPS (EU):

- 34110AN021_AN031.pk2
    - output/34110AN021_AN031/eps_RM11FE00.mot appears to be a section of it
- appears to be a [Renesas v850](https://en.wikipedia.org/wiki/V850)
    - in IDA: NECv850