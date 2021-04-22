import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import numpy as np
from PIL import Image

class FeatureExtractor:
    def __init__(self):
        base_model = tf.keras.applications.EfficientNetB3(include_top = False)
        inputs = tf.keras.layers.Input([224, 224, 3], dtype = tf.uint8)
        model = base_model(inputs)
        model = tf.keras.layers.GlobalAveragePooling2D()(model)
        model = tf.keras.layers.experimental.preprocessing.Normalization()(model)
        self.model = tf.keras.models.Model(inputs = inputs, outputs = model)
        for layer in self.model.layers:
            layer.trainable = False
        self.model.summary()

    def __preprocess_img(self, img):
        img = np.array(img)
        img = tf.image.resize(img, [224, 224])
        img = tf.cast(img, tf.float32)
        img = tf.keras.applications.efficientnet.preprocess_input(img)
        img = tf.expand_dims(img, axis = 0)
        return img

    def get_features(self, img):
        img = self.__preprocess_img(img)
        result = self.model(img)
        result = np.array(result).reshape([-1])
        return result

if __name__ == "__main__":
    img_path = "/home/aleks/insta-project/bmw/0KOMY6JHRZ/2021-03-03_12-15-49_UTC.jpg"
    img = Image.open(img_path)
    extractor = FeatureExtractor()
    result = extractor.get_features(img)
    print(result)

