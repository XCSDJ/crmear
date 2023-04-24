'''
本模块是用于链接到文件服务器，创建s3桶用于保存图像数据,其中put_object()用于上传图片
桶可以直接理解为文件夹
'''

import io
import cv2
import json
import time
from datetime import datetime
from minio import Minio
from minio.lifecycleconfig import LifecycleConfig, Rule, Expiration
from minio.commonconfig import ENABLED, Filter


def create_public_expiring_bucket(client, bucket_name, days):
    if client.bucket_exists(bucket_name):
        return
    client.make_bucket(bucket_name)
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                "Resource": f"arn:aws:s3:::{bucket_name}",
            },
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
            },
        ],
    }
    client.set_bucket_policy(bucket_name, json.dumps(policy))
    config = LifecycleConfig(
        [
            Rule(
                ENABLED,
                rule_filter=Filter(""),
                rule_id="expire in 2 days",
                expiration=Expiration(days=days),
            )
        ]
    )
    client.set_bucket_lifecycle(bucket_name, config)


def gbn(ts, qr):
    ts_minute = datetime.fromtimestamp(ts).strftime("%Y%m%d_%H%M")
    return "{}-{}.jpg".format(ts_minute, qr)


def put_object(client, bucket_name, id_, payload):
    ob = client.put_object(
        bucket_name,
        id_,
        io.BytesIO(payload),
        len(payload),
        content_type="image/jpeg",
    )
    return ob.object_name

def main():
    # 现场ip
    s3ip = "192.168.10.47"
    s3port = "9000"
    bucket = "image"
    s3 = Minio(f"{s3ip}:{s3port}", "admin", "password", secure=False)
    create_public_expiring_bucket(s3, bucket, 60)
    im = cv2.imread("error/tmp1wuiqzo_.png")
    im_bytes = cv2.imencode(".jpg", im)[1].tobytes()
    put_object(s3, "image", "11#炉 机侧废气盘 44", im_bytes)
    put_object(s3, "image", "11#炉 拷克60", im_bytes)

    key = put_object(s3, bucket, im_name, im_bytes)
    imageUrl = f"http://{s3ip}:{s3port}/{bucket}/{quote(key)}"


if __name__ == "__main__":
    main()
