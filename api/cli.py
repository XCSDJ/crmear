import sys
import json
from base64 import b64encode
from urllib import request


# check status
ip = "192.168.10.105"
base_url = "http://{}:8087/vehicle-inspection/digitalCamera/{}"
url = base_url.format(ip, "status")
resp = request.urlopen(url)
ret = json.loads(resp.read())

# start ocr worker is not started
if not ret["active"]:
    url = base_url.format(ip, "start")
    resp = request.urlopen(url)
    ret = json.loads(resp.read())
    print(ret["pid"])

# ocr
# read contents but dont decode
jpg = open(sys.argv[1], "rb").read()
url = base_url.format(ip, "image")
headers = {"Content-Type": "application/json"}
data = {"key": "ocr.bluetron.cn"}
data["image"] = b64encode(jpg).decode()
bindata = json.dumps(data).encode()
req = request.Request(url, bindata, headers)
resp = request.urlopen(req)
ret = json.loads(resp.read())
if ret["exitCode"] == 0:
    for result in ret["results"]:
        word = result["word"]
        polygon = result["polygon"]
        print("{} at {}".format(word, polygon))
else:
    print("exitCode: {exitCode}, errorMessage: {errorMessage}".format_map(ret))
# polygon is [x1, y1, x2, y2, .... xn, yn]
