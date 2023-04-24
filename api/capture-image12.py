# This file is a twelve-angle graph, sent to kafka
# 6	十二视角图	multi_view.jpg
# 7	十二视角图(左前轮)	front_left_wheel.jpg
# 8	十二视角图(右前轮)	front_right_wheel.jpg
# 9	十二视角图(左后轮)	back_left_wheel.jpg
# 10	十二视角图(右后轮)     back_right_wheel.jpg
# 11	十二视角图(左前灯)	front_left_light.jpg
# 12	十二视角图(右前灯)	front_right_light.jpg
# 13	十二视角图(左后灯)	back_left_light.jpg
# 14	十二视角图(右后灯)	back_right_light.jpg
# 15	十二视角图(左前45度)	front_left.jpg
# 16	十二视角图(右前45度)	front_right.jpg
# 17	十二视角图(左后45度)	back_left.jpg
# 18	十二视角图(右后45度)	back_right.jpg
import io
import locale
import os
import subprocess
import sys
import cv2
import time
import json
import numpy as np
from minio import Minio
from s3 import put_object
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PyV4L2Camera.camera import Camera
from PyV4L2Camera.controls import ControlIDs
# Remote file service parameter Settings
sWIDTH_6IN,HEIGHT_6IN = 1800, 1200
FONT = ImageFont.truetype("./simkai.ttf",40,encoding="utf-8")
KAFAKA_HOST = "192.168.10.47"  # 服务器端口地址
KAFAKA_PORT = 9092  # 端口号
KAFAKA_TOPIC_REQUEST = "mv_message_request"
KAFAKA_TOPIC_RESPONSE = "mv_message_response"
KEY = "photo"
s3ip = "192.168.10.47"
s3port = "9000"
bucket = "image"
# class  Get_twelve_photo():
#     def __init__(self):
#         self.producer = kafka_server.Report(KAFAKA_HOST, KAFAKA_PORT, KAFAKA_TOPIC_RESPONSE, KEY)
#         self.consumer = kafka_server.Kafka_consumer(KAFAKA_HOST, KAFAKA_PORT, KAFAKA_TOPIC_REQUEST, "picture", KEY)
#         self.s3 = Minio(f"{s3ip}:{s3port}", "admin", "password", secure=False)

    
#put_object(s3,"vehicle-inspection-file",f"/{vin}/print.jpg",print_img1)




camera_1 = Camera('/dev/video3', 1280,720)
camera_2 = Camera('/dev/video5', 1280,720)
# controls = camera.get_controls()
# camera.set_control_value(ControlIDs.BRIGHTNESS, 48)
index = 0
# print("ok")
# exit()

k = 30
while 1:
    start = time.time()
    frame_1 = camera_1.get_frame()
    frame_2 = camera_2.get_frame()
    # Decode the image
    im_1 = Image.frombytes('RGB', (camera_1.width, camera_1.height), frame_1, 'raw',
                         'RGB')
    im_2 = Image.frombytes('RGB', (camera_2.width, camera_2.height), frame_2, 'raw',
                         'RGB')
    # Convert the image to a numpy array and back to the pillow image
    img1 = cv2.cvtColor(np.asarray(im_1),cv2.COLOR_RGB2BGR)
    img2 = cv2.cvtColor(np.asarray(im_2),cv2.COLOR_RGB2BGR)
    img3=cv2.hconcat([img1,img2])
    dst = cv2.resize(img3,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_LINEAR)
    # im = Image.fromarray(numpy.uint8(arr))
    cv2.imshow("read_img",dst)
    end = time.time()
    if k==0:
        fps = 1/(end-start)
        print("\r fps= {}".format(fps),end="")
        k==30
    k-=1
    # Display the image to show that everything works fine
    
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    elif cv2.waitKey(1) & 0xFF == ord('w'):
            cv2.imwrite(f'../images/{index}.jpg',img)
            index+=1

camera.close()

#十二视角服务模块

