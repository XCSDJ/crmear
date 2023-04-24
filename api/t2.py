'''
import gphoto2 as gp
from subprocess import Popen, PIPE

camera = gp.Camera()
camera.init()
ffmpeg = Popen(['ffmpeg', '-i', '-', '-vcodec', 'rawvideo', '-pix_fmt', 'yuv420p', '-f', 'v4l2', '/dev/video1'], stdin=PIPE)

while True:
  capture = camera.capture_preview()
  filedata = capture.get_data_and_size()
  data = memoryview(filedata)
  ffmpeg.stdin.write(data.tobytes())
'''
import time
import subprocess
import signal, os

def killgphoto2():
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out,err = p.communicate()
    for line in out.splitlines():
        if b'gvfsd-gphoto2' in line:
            print('99')
            #kill process
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)

def record_video():
    subprocess.run(["gphoto2", "--capture-image-and-download","--filename", "tets6.jpg"])
    #subprocess.run(["gphoto2", "--set-config", "movie=1"])
    #subprocess.run(["gphoto2", "--wait-event", "10s"])
    #subprocess.run(["gphoto2", "--set-config", "movie=0"])

if __name__ == '__main':
    killgphoto2()
#record_video()