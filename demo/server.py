from kafka import KafkaConsumer
from kafka import KafkaProducer
import datetime
import config
import json
import numpy as np

producer = KafkaProducer(
    bootstrap_servers   = config.servers,
    api_version         = config.api_version,
    sasl_plain_username = config.username,
    sasl_plain_password = config.password,
    security_protocol   = config.security_protocol,
    sasl_mechanism      = config.sasl_mechanism,
    value_serializer    = config.value_serializer
)
consumer = KafkaConsumer(
    '{}-request'.format(config.username),
    bootstrap_servers   = config.servers,
    api_version         = config.api_version,
    sasl_plain_username = config.username,
    sasl_plain_password = config.password,
    security_protocol   = config.security_protocol,
    sasl_mechanism      = config.sasl_mechanism,
    value_deserializer  = config.value_deserializer
)

print(consumer)
print(producer)

for msg in consumer:
    resp = json.loads(msg.value)
    data = {}
    data['hash'] = resp['hash']
    arr = np.array(resp['img'])

    # todo: add model code here
    print(arr.shape)
    data['result'] = ['previq', 'vtoroi', 'treti', 'chetv', 'pyat']

    producer.send('{}-response'.format(config.username), json.dumps(data))
