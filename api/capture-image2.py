#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2015-22  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import io
import logging
import locale
import os
import subprocess
import sys
import time
import gphoto2 as gp
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
from struct import pack, unpack
from importlib import import_module
#THIS_DIR = os.path.abspath(os.path.dirname(os.path.normpath(__file__)))
#6寸照片模板
WIDTH_6IN,HEIGHT_6IN = 1800, 1200

FONT = ImageFont.truetype("./simkai.ttf",40,encoding="utf-8")
KAFAKA_HOST = "192.168.10.47"  # 服务器端口地址
KAFAKA_PORT = 9092  # 端口号
KAFAKA_TOPIC_REQUEST = "mv_message_request"
KAFAKA_TOPIC_RESPONSE = "mv_message_response"
KEY = "photo"

def get_one_frame(message):
    for msg in message:
        msg = msg.value.decode('utf-8')
        #data = json.load(msg)
        if msg.has_key("photo"):
            return True, msg
        else:
            return False,{}

def main():

    fd_in,fd_out = sys.stdin.fileno(), sys.stdout.fileno()
    #locale.setlocale(locale.LC_ALL, '')
    #logging.basicConfig(
    #format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    #callback_obj = gp.check_result(gp.use_python_logging())
    #producer = kafka_server.Kafka_producer(KAFAKA_HOST, KAFAKA_PORT, KAFAKA_TOPIC_RESPONSE, KEY)
    #consumer = kafka_server.Kafka_consumer(KAFAKA_HOST, KAFAKA_PORT, KAFAKA_TOPIC_REQUEST, None, KEY)
    camera = gp.Camera()
    camera.init()
    ok = True
    print('**************************')
    while True:
        time.sleep(0.1)
        #ok, msg = get_one_frame(consumer.consume_data())
        if ok:
            buf = os.read(fd_in, 4)
            len_ = unpack("I", buf)[0]
            data = os.read(fd_in, len_)
            vin = data.decode('utf-8')
            try:
                #dataId = "123"
                #dataId, vin, config = msg["dataId"], msg["vin"], msg["config"]
                #resize_w,resize_h = config["length"], config["width"]
                file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
                #target = os.path.join('/tmp', file_path.name)
                camera_file = camera.file_get(
                    file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
                file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
                image = Image.open(io.BytesIO(file_data))
                image = image.resize((1080,759),Image.ANTIALIAS)
                draw = ImageDraw.Draw(image)
                draw.text((389,697), vin, fill=(255,0,0), font=FONT)
                image=image.transpose(Image.ROTATE_90)
                bk = Image.new("RGB",[WIDTH_6IN,HEIGHT_6IN],(255,255,255))
                bk.paste(image,(83,35))
                bk.paste(image,(886,35))
                bk.save('./12.jpg')
                # save pic

                out = {"dataId":True,
                            "vin":vin,
                            "mainImage":True,
                            "printImage":True,
                            "twelveImage":False}
            except Exception:
                logging.exception(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                logging.exception("api: get one frame err")
                out = []

            out = json.dumps(out).encode()
            
            buf = pack("I", len(out))
            os.write(fd_out, buf)
            os.write(fd_out, out)

    camera.exit()
    #return 0

if __name__ == '__main__':
    FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
    logging.basicConfig(level=logging.WARNING, format=FORMAT, filename="ocr-api.log")

    if len(sys.argv) > 1:
        kafka_server = import_module(sys.argv[1])
        try:
            main()
        except Exception:
            logging.exception("api: IPC error")
            pass
    