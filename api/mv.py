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