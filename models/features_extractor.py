import tensorflow as tf
import numpy as np
from PIL import Image

if tf.__version__ != "2.4.1":
    raise Exception("Wrong TF version. Run: pip3 install tensorflow-gpu==2.4.1")

class FeatureExtractor:
    def __init__(self):
        model = tf.keras.applications.MobileNetV3Large()
        output_layer = model.layers[-5].output
        self.model = tf.keras.models.Model(inputs = model.input, outputs = output_layer)
        
    def __preprocess_img(self, img):
        img = np.array(img)
        img = tf.cast(img, tf.float32)
        img = tf.keras.applications.mobilenet_v3.preprocess_input(img)
        img = tf.expand_dims(img, axis = 0)
        return img
    
    def get_features(self, img):
        img = self.__preprocess_img(img)
        result = self.model(img)
        result = np.array(result).reshape([-1])
        return result

if __name__ == "__main__":
    img_path = 'C:/Users/Admin/Downloads/10314e99f61037c5749671b0f254f70e.png'
    img = Image.open(img_path)
    extractor = FeatureExtractor()
    result = extractor.get_features(img)
    print(result)