import os
import tarfile

import requests

URL=os.environ["GRAMMAR_URL"]
OUT_PATH="full-grammar"

r = requests.get(URL, stream=True)
if r.status_code == 200:
    with tarfile.open(fileobj=r.raw) as f:
        f.extractall(OUT_PATH, filter="data") 
else:
    print("Download unsuccessful")
