"""server: start a vision algorithm backend

Usage:
server.py module_name

Example:
server.py ocr_mask_text_spotter

The module should define two functions: initialize and analyse.
Function initialize takes no parameter and do everything as needed to
ensure later calling of function analyse can succeed. Function analyse
takes an argument of type np.ndarray as the image to be processed, and
return a list of dict.

def initialize():
    pass

def analyse(image: np.ndarray):
    return [{"polygon": [0,0, 100,0, 0,100, 100,100], "word": "bluetron"}]
"""

import io
import os
import sys
import json
import logging
from PIL import Image, UnidentifiedImageError
from base64 import b64decode, binascii
from struct import pack, unpack
from flask import Flask, request, jsonify, make_response
from subprocess import Popen, PIPE, check_output
from kafka_ import *
import time
from keys import is_valid_key

ERR_NO_ERROR = 0
ERR_UNEXPECTED = -1
ERR_INVALID_JASON = -2
ERR_MISSING_REQUIRED_FIELDS = -3
ERR_INVALID_KEY = -4
ERR_INVALID_BASE64 = -5
ERR_IPC_ERROR = -6
ERR_UNSUPPORTED_IMAGE_FORMAT = -7
ERR_CORRUPTED_IMAGE = -8
ERR_OVERSIZED_IMAGE = -9

ERROR_MSG = {
    ERR_NO_ERROR: "succeed",
    ERR_UNEXPECTED: "unexpected error",
    ERR_INVALID_JASON: "invalid json",
    ERR_MISSING_REQUIRED_FIELDS: "miss required fields(key, image)",
    ERR_INVALID_KEY: "invalid key",
    ERR_INVALID_BASE64: "invalid base64",
    ERR_IPC_ERROR: "IPC error",
    ERR_UNSUPPORTED_IMAGE_FORMAT: "unsupported image format",
    ERR_CORRUPTED_IMAGE: "corrupted image",
    ERR_OVERSIZED_IMAGE: "image size exceed 4M bytes",
}

APP = Flask("ocr image")
THIS_DIR = os.path.abspath(os.path.dirname(os.path.normpath(__file__)))
ENV = {
    "VIRTUAL_ENV": "/home/rlf/ve3",
    "PATH": None,
    "PWD": THIS_DIR,
    "LD_LIBRARY_PATH": os.environ.get("LD_LIBRARY_PATH", ""),
}
OCR = None
# Digitial Camera
DC = None
FD_IN = None
FD_OUT = None
LOG_CMD = ["tail", "dc-server.log"]

_4M = 4 * 1024 * 1024
_MIN_HW = 512
_MAX_HW = 4096


def _make_digitalCamera_response(err, out,dataId):
    # return {"exitCode": err, "errorMessage": ERROR_MSG[err], "results": out}
    out["dataId"]=dataId
    return out


def _is_backend_functional():
    if DC is None:
        return False
    if DC.poll() is not None:
        DC.wait()
        return False
    return True


def _start_backend():
    global DC, FD_IN, FD_OUT
    if not _is_backend_functional():
        os.chdir(THIS_DIR)
        DC = Popen(["python3", "capture-image.py", BACKEND], env=ENV, stdin=PIPE, stdout=PIPE)


def _stop_backend():
    global DC
    if DC is not None:
        DC.communicate()
        DC.kill()
        DC = None
@APP.route("/vehicle-inspection/digitalCamera/start", methods=["GET"])
def digitalCamera_start():
    _start_backend()
    print({"pid": DC.pid})
    return jsonify({"pid": DC.pid})

@APP.route("/vehicle-inspection/digitalCamera/stop", methods=["GET"])
def digitalCamera_stop():
    cmd = f"kill {DC.pid}"
    out = os.popen(cmd)
    return "backend stopped"
@APP.route("/vehicle-inspection/digitalCamera/restart", methods=["GET"])
def digitalCamera_restart():
    global DC
    if DC is not None:
        cmd = f"kill {DC.pid}"
        out = os.popen(cmd)
        DC = Popen(["python3", "capture-image.py", BACKEND], env=ENV, stdin=PIPE, stdout=PIPE)
    return "restart secceed"

@APP.route("/vehicle-inspection/digitalCamera/shutdown", methods=["GET"])
def digitalCamera_shutdown():
    _stop_backend()
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    return "server shut down"
@APP.route("/vehicle-inspection/digitalCamera/checkcamera", methods=["GET"])
def digitalCamera_check():
    cmd = "gphoto2 --auto-detect"
    out = os.popen(cmd)
    informatization=''
    k = 0
    for i in out:
        if k==2:
              informatization =str(i)
              x = informatization.find('usb')
              s1= informatization[:x]
        else:
            k+=1
    
    try:
        l =s1.split()
        out = {"cameraName":l[0],"cameraModel":l[2]}
        return out
    except:
         return    'error: Camera not connected!!'

@APP.route("/vehicle-inspection/digitalCamera/status", methods=["GET"])
def digitalCamera_status():
    return jsonify({"active": _is_backend_functional()})


@APP.route("/vehicle-inspection/digitalCamera/log", methods=["GET"])
def digitalCamera_log():
    os.chdir(THIS_DIR)
    log = check_output(LOG_CMD)
    response = make_response(log.decode())
    response.headers["context-type"] = "text/plain"
    return response


def _get_one_digitalCamera_image(vin_code):
    """main logic of ocr image

    return tuple of code and output"""
    out = []
    try:
        buf = vin_code.encode('utf-8')
    except binascii.Error:
        return ERR_INVALID_BASE64, out

    if len(buf) > _4M:
        return ERR_OVERSIZED_IMAGE, out
    '''
    try:
        print("******************")
        Image.open(io.BytesIO(buf)).convert("RGB")
    except UnidentifiedImageError:
        return ERR_UNSUPPORTED_IMAGE_FORMAT, out
    except OSError:
        return ERR_CORRUPTED_IMAGE, out
    '''
    
    try:
        os.write(FD_OUT, pack("I", len(buf)))
        os.write(FD_OUT, buf)
        len_ = unpack("I", os.read(FD_IN, 4))[0]
        out = os.read(FD_IN, len_)
        out = json.loads(out)
    except (IOError, json.JSONDecodeError):
        return ERR_IPC_ERROR, out
    return ERR_NO_ERROR, out

##{"key":"X-AI", "vin":"LVAV2AVB7NE231883"}
@APP.route("/vehicle-inspection/digitalCamera/image", methods=["POST"])
def get_one_digitalCamera_image():
    _start_backend()
    return 'ok'
    try:
        data = json.loads(request.data)
        #data = {"key":"X-AI","vin":"LVAV2AVB7NE231883"}
    except json.JSONDecodeError:
        return jsonify(_make_digitalCamera_response(ERR_INVALID_JASON, []))
    if not ("key" in data and "vin" in data):
        return jsonify(_make_digitalCamera_response(ERR_MISSING_REQUIRED_FIELDS, []))
    if is_valid_key(data["key"]):
        return jsonify(_make_digitalCamera_response(*_get_one_digitalCamera_image(data["vin"]),data["dataId"]))
    else:
        return jsonify(_make_digitalCamera_response(ERR_INVALID_KEY, []))

# init kafka & getFrame
def init():
    
    APP.debug = False  
    APP.use_reloader = False
    ve = ENV["VIRTUAL_ENV"]
    ve_bin = os.path.join(ve, "bin")
    path = os.getenv("PATH")
    if path.find(ve_bin) == -1:
        path = "{}:{}".format(ve_bin, path)
    ENV["PATH"] = path
    _start_backend()



if __name__ == "__main__":
    FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
    logging.basicConfig(level=logging.WARNING, format=FORMAT, filename="dc-server.log")
    if len(sys.argv) < 2:
        print("Usage: {} module_name".format(sys.argv[0]))
        sys.exit(-1)
    BACKEND = sys.argv[1]
    init()
    APP.run("0.0.0.0", threaded=True,port=8099)
