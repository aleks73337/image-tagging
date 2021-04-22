import os
import json

class DatasetParser:
    def __init__(self, data_folder : str):
        self.data_folder = data_folder
        self.meta_data = self.get_meta_data()
        self.imgs_paths, self.tags = self.get_img_paths_with_tags()

    def get_meta_data(self):
        meta_fname = os.path.join(self.data_folder, '_meta.json')
        with open(meta_fname, 'r') as f:
            meta_data = f.read()
        meta_data = json.loads(meta_data)
        meta_data = meta_data.get('data')
        return meta_data

    def get_img_paths_with_tags(self):
        imgs_paths = []
        tags = []
        for el in self.meta_data:
            img_id = el.get('id')
            img_fname = os.path.join(self.data_folder, img_id + '.jpg')
            img_tag = el.get('tags')
            imgs_paths.append(img_fname)
            tags.append(img_tag)
        return imgs_paths, tags
