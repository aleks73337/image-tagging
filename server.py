from kafka import KafkaConsumer
from kafka import KafkaProducer
from models.detector import Detector
from models.place_classifier import PlaceClassifier
from models.features_extractor import FeatureExtractor
from models.closest_pictures_model import ClosestPicturesModel
from PIL import Image
import datetime
import demo.config as config
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

placer = PlaceClassifier()
print(placer)

feacher = FeatureExtractor()
print(feacher)

closest = ClosestPicturesModel()
print(closest)

detector = Detector()
print(detector)

def get_places(arr):
    result, _ = placer.predict(np.uint8(arr))
    return [key for key in result]

for msg in consumer:
    resp = json.loads(msg.value)
    data = {}
    data['hash'] = resp['hash']
    arr = np.array(resp['img'])

    print(arr.shape)

    img = Image.fromarray(np.uint8(arr))

    features = feacher.get_features(img)
    features = features.reshape(1, -1)
    result  = closest.predict(features)[0]
    result += detector.get_objects_on_img(img)
    result += get_places(arr)
    print(result)
    data['result'] = result

    producer.send('{}-response'.format(config.username), json.dumps(data))
