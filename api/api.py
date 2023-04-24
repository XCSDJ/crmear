import io
import os
import sys
import json
import numpy as np
import logging
from PIL import Image, ImageOps
from struct import pack, unpack
from importlib import import_module


def main():
    mod.initialize()
    fd_in, fd_out = sys.stdin.fileno(), sys.stdout.fileno()
    while True:
        buf = os.read(fd_in, 4)
        len_ = unpack("I", buf)[0]
        data = os.read(fd_in, len_)

        im = Image.open(io.BytesIO(data)).convert("RGB")
        im = np.array(ImageOps.exif_transpose(im))
        try:
            out = mod.analyse(im)
        except Exception:
            logging.exception("api: ocr error")
            out = []
        out = json.dumps(out).encode()

        buf = pack("I", len(out))
        os.write(fd_out, buf)
        os.write(fd_out, out)
if __name__ == '__main__':
    FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
    logging.basicConfig(level=logging.WARNING, format=FORMAT, filename="ocr-api.log")
    if len(sys.argv) > 1:
        mod = import_module(sys.argv[1])
        try:
            main()
        except Exception:
            logging.exception("api: IPC error")
            pass
