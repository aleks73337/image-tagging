from joblib import load
import numpy as np
import pandas as pd
import ast
from collections import Counter

class ClosestPicturesModel:
    def __init__(self):
        model_path = 'image_features_knn.joblib'
        tags_path = 'tags.csv'
        self.model = load(model_path)
        self.tags = self.__get_tags(tags_path)

    def __get_tags(self, tags_path, encoding='utf-8'):
        df = pd.read_csv(tags_path, index_col = 0)
        tags = []
        for idx, el in df.iterrows():
            el = el['tags']
            list_tags =  ast.literal_eval(el)
            tags.append(list_tags)
        return tags

    def __filter_by_distance(self, distanses, idxs, max_dist : float):
        result = []
        for dist, idx in zip(distanses, idxs):
            result.append(idx)
        return result

    def __get_tags_by_indexes(self, idxs, imgs_with_tag):
        tags = [el for i in idxs for el in self.tags[i]]
        counters = Counter(tags)
        result = []
        for tag, counter in counters.items():
            if counter >= imgs_with_tag:
                result.append(tag)
        return result

    ###
    # features - the output of feature extractor model
    # imgs_with_tag - if number of images with the same tag >= n_tags, the tag is appended to the answer
    # max_distance - max distance between knn vectors. 
    def predict(self, features, imgs_with_tag : int = 2, max_distance : float = 200.0):
        distanses_batch, idxs_batch = self.model.kneighbors(features, return_distance = True)
        result = []
        for distanses, idxs in zip(distanses_batch, idxs_batch):
            valid_idxs = self.__filter_by_distance(distanses, idxs, max_distance)
            tags = self.__get_tags_by_indexes(valid_idxs, imgs_with_tag)
            result.append(tags)
        return result

if __name__ == "__main__":
    model = ClosestPicturesModel()
    img = np.random.uniform(low = 0, high = 1, size = [1, 1536])
    tags = model.predict(img)
    print(tags)

