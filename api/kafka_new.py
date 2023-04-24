import json
from kafka import KafkaProducer
import time
# producer
class Report:
    def __init__(self, ip,port,topic, key):
        self.uuid = bytes(key, "utf8")
        self.topic = topic
        self.server = "{}:{}".format(ip, port)
        self.out = None
    def __call__(self, map_):
        # if map_["patrolResult"] == 2:
        #     return
        value = bytes(json.dumps(map_), "utf8")
        if self.out is None:
            self.out = KafkaProducer(
                bootstrap_servers=[self.server], api_version=(0, 10, 1)
            )
        self.out.send(self.topic, key=self.uuid, value=value)
#consumer



# map_ = {"1":"2313212", "ts":123432}
# report(map_)
# print('ok')
