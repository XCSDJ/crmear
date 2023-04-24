import json
from kafka import KafkaProducer

import time
class Report:
    def __init__(self, kcfg, scfg):
        self.uuid = bytes(scfg["uuid"], "utf8")
        self.topic = kcfg["topic"]
        self.server = "{}:{}".format(kcfg["ip"], kcfg["port"])
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
kcfg = {
"topic":"mv_message_response",
"ip":"192.168.10.47",
"port":"9092"

}
cfg0={"uuid":"photo"}
report = Report(kcfg, cfg0)
map_ = {"1":"2313212", "ts":123432}
while 1:
    time.sleep(1)
    report(map_)
    print('ok')