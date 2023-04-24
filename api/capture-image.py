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
import cv2
import time
import gphoto2 as gp
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from struct import pack, unpack
from importlib import import_module
from copy import deepcopy
from s3 import put_object
from minio import Minio
from threading import Thread
#THIS_DIR = os.path.abspath(os.path.dirname(os.path.normpath(__file__)))
#6寸照片模板
WIDTH_6IN,HEIGHT_6IN = 1800, 1200
FONT = ImageFont.truetype("./simkai.ttf",40,encoding="utf-8")
KAFAKA_HOST = "192.168.10.47"  # 服务器端口地址
KAFAKA_PORT = 9092  # 端口号
KAFAKA_TOPIC_REQUEST = "mv_message_request"
KAFAKA_TOPIC_RESPONSE = "mv_message_response"
KEY = "photo"
s3ip = "192.168.10.47"
s3port = "9000"
bucket = "image"

#错误码
ERR_NO_ERROR = 0
ERR_INVALID_JASON = -1
ERR_NO_CAMERA = -2  
ERR_CAMERA_ERR = -3
ERR_PICTURE_ERR=-4
ERR_BYTE_PICTURE=-5
ERR_SAVE_PICTURE=-6

ERROR_MSG = {
    ERR_NO_ERROR: "succeed",
    ERR_INVALID_JASON: "invalid json",
    ERR_NO_CAMERA: "unconnected camera",
    ERR_CAMERA_ERR:"Image capture failed, please try again",
    ERR_PICTURE_ERR:"Processing picture error please try again",
    ERR_BYTE_PICTURE:"Image transcoding failed, please try again",
    ERR_SAVE_PICTURE:"Failed to save the picture, please try again"


    
    
}
def error_return(err,out):
    return { "exitCode": err, "errorMessage": ERROR_MSG[err],"results": out}
class Get_image():
    def __init__(self):
        self.camera = gp.Camera()
        self.camera.init()
        self.file_path = None
        self.camera_file =None
        self.file_data = None
    def get_one_photo(self,GP_CAPTURE_IMAGE,GP_FILE_TYPE_NORMAL):
        self.file_path = self.camera.capture(GP_CAPTURE_IMAGE)
        self.camera_file = self.camera.file_get(self.file_path.folder, self.file_path.name, GP_FILE_TYPE_NORMAL)
        self.file_data = gp.check_result(gp.gp_file_get_data_and_size(self.camera_file))
        return self.file_data
    def get_one_message(self,message):
        for msg in message:
            if msg.key==b"photo":
                data = json.loads(msg.value.decode('utf-8'))
                return  True,data
            else:
                return  False,{}
    def get_full_image(self,file_data,vin,resize_w,resize_h):
        w =1080
        h = 759
        image = Image.open(io.BytesIO(file_data))
        image = image.resize((w,h),Image.ANTIALIAS)
        img_original=deepcopy(image)
        img_min = image.resize((w//3, h//3), Image.LANCZOS)
        draw = ImageDraw.Draw(image)
        draw.text((389,697), vin, fill=(255,0,0), font=FONT)
        image=image.transpose(Image.ROTATE_90)
        img_print = Image.new("RGB",[WIDTH_6IN,HEIGHT_6IN],(255,255,255))
        img_print.paste(image,(83,35))
        img_print.paste(image,(int(h)+137,35))
        
        return img_print,img_original,img_min
    def get_byte_image(self,img):
        img_pil = cv2.cvtColor(np.asarray(img),cv2.COLOR_RGB2BGR)
        img_byte= cv2.imencode(".jpg", img_pil)[1].tobytes()
        return img_byte


def main():
    # while 1:
    #     try:
    producer = kafka_server.Report(KAFAKA_HOST, KAFAKA_PORT, KAFAKA_TOPIC_RESPONSE, KEY)
    s3 = Minio(f"{s3ip}:{s3port}", "admin", "password", secure=False)
    consumer = kafka_server.Kafka_consumer(KAFAKA_HOST, KAFAKA_PORT, KAFAKA_TOPIC_REQUEST, "picture", KEY)
    print(2)
    #     break
    # except:
    #     time.sleep(1)
# while True:
#     try:
    get_img=Get_image()
        #     print(3)
        #     break
        # except:
        #     producer(error_return(ERR_NO_CAMERA,{}))
        #     time.sleep(2)
    while True:
        try:
            time.sleep(0.1)
            ok, msg = get_img.get_one_message(consumer.consume_data())
            print(4)
        except:
            producer(error_return(ERR_NO_CAMERA,{}))
            time.sleep(2)
            continue

        if ok:
            try:
                vin, config = msg["vin"], msg["config"]
                resize_w,resize_h = config["height"], config["width"]
            except:
                producer(error_return(ERR_INVALID_JASON,{}))
                time.sleep(2)
                continue
            # try:
            #     #get_one_photo
            print("sssss1")
            file_data = get_img.get_one_photo(gp.GP_CAPTURE_IMAGE,gp.GP_FILE_TYPE_NORMAL)
            print(1,"ok")
            # except:
            #     producer(error_return(ERR_CAMERA_ERR,{}))
                
            #     time.sleep(2)
            #     continue
            try:
                #get_full_image
                print_img,original_img,min_img = get_img.get_full_image(file_data,vin,resize_w,resize_h)
                print(2,"ok")
            except:
                producer(error_return(ERR_PICTURE_ERR,{}))
                
                time.sleep(2)
                continue
            try:
                #get_byte_image
                print_img1 = get_img.get_byte_image(print_img)
                main_img = get_img.get_byte_image(original_img)
                min_img = get_img.get_byte_image(min_img)
                print(3,"ok")
            except:
                producer(error_return(ERR_BYTE_PICTURE,{}))
                
                time.sleep(2)
                continue
            try:
                # save photo
                put_object(s3,"vehicle-inspection-file",f"/{vin}/digital_camera_print_image.jpg",print_img1)
                put_object(s3,"vehicle-inspection-file",f"/{vin}/digital_camera_main_image.jpg",main_img)
                put_object(s3,"vehicle-inspection-file",f"/{vin}/digital_camera_main_thumbnail.jpg",min_img)
                print(4,"ok")
            except:
                producer(error_return(ERR_SAVE_PICTURE,{}))
                time.sleep(2)
                continue
                
            out = {
                        "vin":vin,
                        "digitalCameraMainImage":True,
                        "digitalCameraPrintImage":True,
                        "twelveViewImage":False}
            
            try:
            
                producer(error_return(ERR_NO_ERROR,out))
                print('push kafka successfully!!')
            except:
                pass
    try:
        get_img.camera.exit()
    except:
        pass
    

if __name__ == '__main__':
    if len(sys.argv) > 1:
        kafka_server = import_module(sys.argv[1])
        
        try:
            print(1)
            main()
        except Exception:
            logging.exception("api: IPC error")
            pass
    #for i in range(20):
    #    os.popen("gphoto2--capture-image-and-download")