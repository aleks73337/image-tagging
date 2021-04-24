from kafka import KafkaProducer
from kafka import KafkaConsumer
import config
import json
import base64
import hashlib
import numpy as np
import cv2
import threading

class Request:
    def __init__(self):
        self._producer = KafkaProducer(
            bootstrap_servers   = config.servers,
            api_version         = config.api_version,
            sasl_plain_username = config.username,
            sasl_plain_password = config.password,
            security_protocol   = config.security_protocol,
            sasl_mechanism      = config.sasl_mechanism,
            value_serializer    = config.value_serializer
        )
        self._consumer = KafkaConsumer(
            '{}-response'.format(config.username),
            bootstrap_servers   = config.servers,
            api_version         = config.api_version,
            sasl_plain_username = config.username,
            sasl_plain_password = config.password,
            security_protocol   = config.security_protocol,
            sasl_mechanism      = config.sasl_mechanism,
            value_deserializer  = config.value_deserializer
        )
        self._hash = ""
        self._evnt = threading.Event()
        self._cache = {}
        def consumer_thread(self):
            for msg in self._consumer:
                resp = json.loads(msg.value)
                print(resp)
                if self._evnt.is_set() or resp['hash'] != self._hash:
                    continue
                self._result = resp['result']
                self._cache[resp['hash']] = self._result
                self._evnt.set()
        self._thread = threading.Thread(target=consumer_thread, args=[self])
        self._thread.daemon = True
        self._thread.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self._thread.exit()

    def send_img(self, image):
        image = np.array(image)
        image = cv2.resize(image, dsize=(224, 224), interpolation=cv2.INTER_CUBIC)

        data = {}
        data['hash'] = hashlib.md5(image.tobytes()).hexdigest()
        if data['hash'] in self._cache:
            return self._cache[data['hash']]

        data['img'] = np.array(image).tolist()
        string_data = json.dumps(data)

        self._hash = data['hash']
        self._evnt.clear()
        print('Sending message size: {}'.format(len((string_data))))
        print(self._producer.send('{}-request'.format(config.username), string_data))

    def await_tags(self):
        timeout=30
        if self._evnt.wait(timeout=timeout):
            return self._result
        print("Tags wait timeout {} sec".format(timeout))
