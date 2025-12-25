from flask import request
from uuid import uuid4
import os

BASIC_WRITER_PATH = "uploads"

def basicFileWriter(keys: list[str]):
  keyPaths = {}
  filenames = list(request.files)

  for k in filenames:
    file = request.files.get(k)
    if (file == None): continue
    if (file.filename == ""): continue

    # generate unique filenames to prevent overwrites
    fwpath = os.path.join(BASIC_WRITER_PATH, str(uuid4()) + file.filename)
    file.save(fwpath)
    keyPaths[k] = fwpath

  return keyPaths