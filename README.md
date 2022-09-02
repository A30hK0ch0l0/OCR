## Install

`PROJECT_DIR` is project root

```bash
mkdir ${PROJECT_DIR}
cd ${PROJECT_DIR}

sudo apt update -y
sudo apt install -y python3 python3-venv git
sudo apt install -y python-opencv tesseract-ocr poppler-utils

git clone http://185.208.77.246/inference/ocr.git .
# git checkout develop

python3 -m venv venv
source venv/bin/activate
pip install -U pip wheel setuptools pytest
pip install -r requirements.txt
```

## Test

```bash
bin/test.sh

## OR
# source venv/bin/activate
# pytest
```

## Install package in other projects

```bash
pip install git+http://185.208.77.246/inference/ocr.git
```

## User manual

Every pdf file before passing to the project must remove images from it.

for doing that for each one must run command like this:

"bin/gs -o XXX -sDEVICE=pdfwrite -dFILTERIMAGE -dFILTERVECTOR YYY"

that, XXX is output address and YYY is input address

```python
from lfocr import ocr
import json

temp = ocr()
json_result = temp.process('afkar_test.pdf', 'afkar')
with open('afkar_text_output.json', 'w') as output:
    json.dump(json_result, output, ensure_ascii=False)
```
