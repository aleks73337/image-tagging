import os

class DatasetParser:
    def __init__(self, data_folder : str):
        self.data_folder = data_folder
        self.meta_data = self.get_meta_data()
        self.imgs_paths, self.tags = self.get_img_paths_with_tags()

    def get_meta_data(self):
        meta_fname = os.path.join(ds_path, '_meta.json')
        with open(meta_fname, 'r') as f:
            meta_data = f.read()
        meta_data = json.loads(meta_data)
        meta_data = meta_data.get('data')
        return meta_data

    def get_img_paths_with_tags():
        imgs_paths = []
        tags = []
        for el in self.meta_data():
            img_id = el.get('id')
            img_fname = os.path.join(self.data_folder, img_id)
            img_tag = el.get('tags')
        return imgs_paths, tags
