import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from PIL import Image
from PIL import ImageOps

if tf.__version__ != "2.4.1":
    raise Exception("Wrong TF version. Run: pip3 install tensorflow-gpu==2.4.1")

class Detector:
    def __init__(self):
        model_url = "https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1"
        self.model = hub.load(model_url).signatures['default']
        self.target_img_width = 620
        self.target_img_height = 480
        
    def __run_detector(self, img):
        img = np.array(img)
        converted_img = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]
        result = self.model(converted_img)
        result = {key:value.numpy() for key,value in result.items()}
        return result
    
    def __resize_img(self, img):
        resized_img = ImageOps.fit(img, (self.target_img_width, self.target_img_height), Image.ANTIALIAS)
        image_rgb = resized_img.convert("RGB")
        return image_rgb
    
    def get_objects_on_img(self, img, n_objects = -1, min_score = 0.1, is_unique = True):
        img = self.__resize_img(img)
        result = self.__run_detector(img)
        scores = result["detection_scores"]
        class_names = result["detection_class_entities"]
        scores_with_classes = zip(scores, class_names)
        scores_with_classes = sorted(scores_with_classes, key = lambda x: x[0], reverse=True)
        if n_objects == -1:
            n_objects = len(scores_with_classes)
        img_classes = list()
        for i in range(n_objects):
            class_name = scores_with_classes[i][1].decode("ascii")
            class_score = scores_with_classes[i][0]
            if class_score < min_score:
                break
            img_classes.append(class_name)
        if is_unique:
            img_classes = list(set(img_classes))
        return img_classes


if __name__ == "__main__":
    img_path = 'C:/Users/Admin/Downloads/10314e99f61037c5749671b0f254f70e.png'
    img = Image.open(img_path)
    detector = Detector()
    result = detector.get_objects_on_img(img)
    print(result)