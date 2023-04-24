import sys
import cv2
import numpy as np
from PIL import Image
from math import degrees, radians, fabs, atan2, sin, cos


from ctpn.ctpn.model import Detector
from crnn.recognizer import Recognizer
from crnn.keys_5990 import alphabet

DET = None
REC = None


def crnnRec(recognizer, im, text_recs):
    results = []
    xDim, yDim = im.shape[1], im.shape[0]

    for rec in text_recs:
        pt1 = (max(1, rec[0]), max(1, rec[1]))
        pt2 = (rec[2], rec[3])
        pt3 = (min(rec[6], xDim - 2), min(yDim - 2, rec[7]))
        pt4 = (rec[4], rec[5])

        degree = degrees(atan2(pt2[1] - pt1[1], pt2[0] - pt1[0]))  # 图像倾斜角度

        partImg = dumpRotateImage(im, degree, pt1, pt2, pt3, pt4)
        # 根据ctpn进行识别出的文字区域，进行不同文字区域的crnn识别
        image = Image.fromarray(partImg).convert("L")
        # 进行识别出的文字识别
        sim_pred = recognizer(image)
        results.append([rec, sim_pred])  # 识别文字
    return results


def dumpRotateImage(img, degree, pt1, pt2, pt3, pt4):
    height, width = img.shape[:2]
    heightNew = int(
        width * fabs(sin(radians(degree))) + height * fabs(cos(radians(degree)))
    )
    widthNew = int(
        height * fabs(sin(radians(degree))) + width * fabs(cos(radians(degree)))
    )
    matRotation = cv2.getRotationMatrix2D((width / 2, height / 2), degree, 1)
    matRotation[0, 2] += (widthNew - width) / 2
    matRotation[1, 2] += (heightNew - height) / 2
    imgRotation = cv2.warpAffine(
        img, matRotation, (widthNew, heightNew), borderValue=(255, 255, 255)
    )
    pt1 = list(pt1)
    pt3 = list(pt3)

    [[pt1[0]], [pt1[1]]] = np.dot(matRotation, np.array([[pt1[0]], [pt1[1]], [1]]))
    [[pt3[0]], [pt3[1]]] = np.dot(matRotation, np.array([[pt3[0]], [pt3[1]], [1]]))
    ydim, xdim = imgRotation.shape[:2]
    imgOut = imgRotation[
        max(1, int(pt1[1])) : min(ydim - 1, int(pt3[1])),
        max(1, int(pt1[0])) : min(xdim - 1, int(pt3[0])),
    ]
    # height,width=imgOut.shape[:2]
    return imgOut


def sort_box(box):
    """
    对box排序,及页面进行排版
    text_recs[index, 0] = x1
        text_recs[index, 1] = y1
        text_recs[index, 2] = x2
        text_recs[index, 3] = y2
        text_recs[index, 4] = x3
        text_recs[index, 5] = y3
        text_recs[index, 6] = x4
        text_recs[index, 7] = y4
    """

    box = sorted(box, key=lambda x: sum([x[1], x[3], x[5], x[7]]))
    return box


def initialize():
    global DET, REC
    DET = Detector("./data/CTPN-CRNN/checkpoints")
    REC = Recognizer("./data/CTPN-CRNN/ab5990-w280-acc989.pth", alphabet)


def analyse(image):
    text_recs, resized = DET(image)
    text_recs = sort_box(text_recs)
    result = crnnRec(REC, resized, text_recs)
    list_of_dict = [{"polygon": p.tolist(), "word": w} for p, w in result]
    return list_of_dict


if __name__ == "__main__":
    initialize()
    image = np.array(Image.open(sys.argv[1]).convert("RGB"))
    for result in analyse(image):
        word = result["word"]
        polygon = result["polygon"]
        print("{} at {}".format(word, polygon))
