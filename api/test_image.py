# from pyv4l2.frame import Frame
# from pyv4l2.control import Control
# from PIL import Image,ImageOps
# import io
import time

# dict_img ={}
# i=0
# frame = Frame('/dev/video2')
# while 1:
#     time.sleep(1)
#     frame_data = frame.get_frame()
#     print('*************')
#     print(frame_data)
# from PyV4L2Camera.camera import Camera

# camera = Camera('/dev/video2')
# while 1:
#  time.sleep(0.01)
#  frame = camera.get_frame()
#  print(frame.decode)

    # im = Image.open(io.BytesIO(frame_data)).convert("RGB")
    # im = np.array(ImageOps.exif_transpose(im))
   
# control = Control("/dev/video2")
# control.get_controls()
# control.get_control_value(9963776)
# control.set_control_value(9963776, 8)
# import cv2
# print(1)
# video = cv2.VideoCapture(3)
# ret,frame=video.read()
# cv2.imwrite('./3.jpg',frame)
# print(2)
# fps = video.get(cv2.CAP_PROP_FPS)
# print(fps)
# size = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)))
# print(size)
# i=0
# dict_img ={}
# while True:
#     ret, frame = video.read()
#     # cv2.imshow("A video", frame)
#     if frame != None:
#         print("\r第{}帧".format(i),f'fps== {fps}',f'ret== {ret}',end='')
#         i+=1
#     c = cv2.waitKey(1)
#     if c == 27:
#         break
# video.release()
# cv2.destroyAllWindows()
# import numpy
# from PIL import Image

# from PyV4L2Camera.camera import Camera
# from PyV4L2Camera.controls import ControlIDs

# controls = camera.get_controls()
# print(2)
# for control in controls:
#     print(control.name)

# camera.set_control_value(ControlIDs.BRIGHTNESS, 48)

# for _ in range(2):
# print(3)
# i = 0
# while 1:
#     camera = Camera('/dev/video2',1920,1080)
#     frame = camera.get_frame()
#     controls = camera.get_controls()
#     print(controls)
        
#         # Decode the image
    
#     im = Image.frombytes('RGB', (camera.width, camera.height), frame, 'raw',
#                             'RGB')
    
#     im.save(f'../images/{i}.jpg')
#     i+=1
#     camera.close()
        # Convert the image to a numpy array and back to the pillow image
    # arr = numpy.asarray(im)
    # im = Image.fromarray(numpy.uint8(arr))

    #     # Display the image to show that everything works fine
    # im.save('1.jpg')
    # -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 19:41:05 2022

@author: user
"""
import cv2
import numpy as np
import threading
import time
from multiprocessing import Process, Queue
import os, time, random

class Camera(threading.Thread):
    __slots__ = ['camera','Flag','count','width','heigth','frame']
    def __init__(self):
        threading.Thread.__init__(self)
        self.camera = cv2.VideoCapture(3)
        self.Flag = 0
        self.count = 1
        self.width = 1920
        self.heigth = 1080
        self.name = ''
        self.path = ''
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,self.width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT,self.heigth)
        #for i in range(46):
            #print("No.={} parameter={}".format(i,self.camera.get(i)))
    def run(self):
        while True:
            ret, self.frame =  self.camera.read() # 摄像头读取,ret为是否成功打开摄像头,true,false。 frame为视频的每一帧图像
            self.frame = cv2.flip(self.frame, 1) # 摄像头是和人对立的，将图像左右调换回来正常显示。
            if self.Flag == 1:
                print("拍照")
                if self.name == ''and self.path == '':
                    cv2.imwrite(str(self.count) + '.jpg', self.frame) #将画面写入到文件中生成一张图片
                elif self.name != '':
                    cv2.imwrite(self.name+ '.jpg', self.frame)
                self.count+=1
                self.Flag = 0
            if self.Flag == 2:
                print("退出")
                self.camera.release()#释放内存空间
                cv2.destroyAllWindows()#删除窗口
                break
            
    def take_photo(self):
        self.Flag = 1
    def exit_program(self):
        self.Flag = 2
    def set_name(self,str):
        self.name = str
    def set_path(self,str):
        self.path = str

def show_window(cap):
        while True:
            cv2.namedWindow("window", 1)# 1代表外置摄像头
            cv2.resizeWindow("window", cap.width,cap.heigth )  #指定显示窗口大小
            cv2.imshow('window', cap.frame)
            c = cv2.waitKey(50) #按ESC退出画面
            if c == 27:
                cv2.destroyAllWindows()
                break

if __name__ == '__main__':
    cap = Camera()
    cap.start()
    while True:
        i = int(input("input:"))
        if i == 1:
            cap.take_photo()
        if i == 2:
            cap.exit_program()
        if i == 3:
            recv_data_thread = threading.Thread(target=show_window,args=(cap,))
            recv_data_thread.start()
        time.sleep(1)



