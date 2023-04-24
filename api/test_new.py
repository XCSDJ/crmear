import os
import sys
import json
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import kafka_
import time

def get_one_frame(message):
    for msg in message:
        print(msg)
        return msg
        # if msg.key==b"photo":
        #     data = json.loads(msg.value.decode('utf-8'))
        #     return  True,data
        # else:
        #     return  False,{}
WIDTH_6IN,HEIGHT_6IN = 1800, 1200
# FONT = ImageFont.truetype("./simkai.ttf",40,encoding="utf-8")
KAFAKA_HOST = "192.168.10.47"  # 服务器端口地址
KAFAKA_PORT = 9092  # 端口号
KAFAKA_TOPIC_REQUEST = "mv_message_request"
KAFAKA_TOPIC_RESPONSE = "mv_message_response"
KEY = "photo"
consumer = kafka_.Kafka_consumer(KAFAKA_HOST, KAFAKA_PORT, KAFAKA_TOPIC_RESPONSE, "picture", KEY)
while True:
        time.sleep(0.1)
        msg = get_one_frame(consumer.consume_data())
        # if ok:
        print(msg.value)
            
            
       
        
        