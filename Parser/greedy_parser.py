import urllib.request
import os
import sys
import json
import re
import logging
from joblib import Parallel, delayed
from multiprocessing import Pool

def patch_http_connection_pool(**constructor_kwargs):
    from urllib3 import connectionpool, poolmanager

    class MyHTTPConnectionPool(connectionpool.HTTPConnectionPool):
        def __init__(self, *args,**kwargs):
            kwargs.update(constructor_kwargs)
            super(MyHTTPConnectionPool, self).__init__(*args,**kwargs)
    poolmanager.pool_classes_by_scheme['http'] = MyHTTPConnectionPool

def patch_https_connection_pool(**constructor_kwargs):
    from urllib3 import connectionpool, poolmanager

    class MyHTTPSConnectionPool(connectionpool.HTTPSConnectionPool):
        def __init__(self, *args,**kwargs):
            kwargs.update(constructor_kwargs)
            super(MyHTTPSConnectionPool, self).__init__(*args,**kwargs)
    poolmanager.pool_classes_by_scheme['https'] = MyHTTPSConnectionPool

patch_http_connection_pool(maxsize=50)
patch_https_connection_pool(maxsize=50)

from tqdm import tqdm

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from Parser.base import Base
from Parser.insta_parser import Parser
from Parser.config import global_config
from Parser.person import Post

tags_regular = re.compile(r'#\w+')

def _get_data(object, required):
    actual_count = len(object.data)
    if actual_count <required:
        object.request_more(required - actual_count)
    return object.data[:required]

class GreedyParser(Base):
    def __init__(self, 
                start_user_name                : str, 
                count_of_posts_per_profile     : int = 100, 
                count_of_following_per_profile : int = 100,
                total_count_of_posts           : int = 500,
                min_tags_per_post              : int =  1,
                folder_to_save_data            : str = os.path.join(parent_dir, 'dataset')):

        super().__init__("GreedyParser")

        self.__parser               = Parser()
        self.__count_of_posts       = count_of_posts_per_profile
        self.__cont_of_following    = count_of_following_per_profile
        self.__total_count_of_posts = total_count_of_posts
        self.__min_tags_per_post    = min_tags_per_post
        self.__folder               = folder_to_save_data
        self.__meta_file_path       = os.path.join(self.__folder, '_meta.json')
        self.__process_user_parallel = Parallel(n_jobs=4, require='sharedmem')

        if not os.path.exists(self.__folder):
            os.makedirs(self.__folder)

        self.__parse(start_user_name)

    def __parse(self, start_user_name : str):
        self.__posts                = []
        self.__requested_users = [start_user_name]

        index = self.__try_to_restore()
        initial_count = len(self.__posts)

        self.__bar = tqdm(total=self.__total_count_of_posts)

        with Parallel(n_jobs=2, require='sharedmem') as parallel:
            skip_save = False
            while index < len(self.__requested_users):
                if len(self.__posts) - initial_count >= self.__total_count_of_posts:
                    break
                tasks = []
                if not skip_save:
                    tasks.append(delayed(self.__save_meta)(index-1, self.__meta_file_path, self.__requested_users, self.__posts))
                tasks.append(delayed(self.__process_user_name)(self.__requested_users[index]))
                skip_save = parallel(tasks)[-1]
                index += 1

        self.__save_meta(index-1, self.__meta_file_path, self.__requested_users, self.__posts)
        self.__bar.close()

        self._logger.info(f"Collected {len(self.__posts) - initial_count} new post")

    def __process_user_name(self, username : str):
        self._logger.debug(f'Request {username}')
        user = self.__parser.request_person(username)
        self.__bar.set_description(f'Current user is {username}')

        if user.is_business_account or user.is_private:
            return False

        objects = self.__process_user_parallel([delayed(_get_data)(user.posts, self.__count_of_posts), 
                                                           delayed(_get_data)(user.follow, self.__cont_of_following)])
                                    
        posts = objects[0]
        users = objects[1]

        new_posts = self.__process_user_parallel(delayed(self.__process_post)(post, self.__min_tags_per_post, self.__folder) for post in posts)
        new_posts = [data for data in new_posts if data]
        self.__posts += new_posts
        count_new_posts = len(new_posts)
        self.__bar.update(count_new_posts)

        for username in users:
            if username not in self.__requested_users:
                self.__requested_users.append(username)

        return count_new_posts != 0
    
    @staticmethod
    def __process_post(post : Post, __min_tags_per_post : int, folder : str):
        if post.is_video:
            return None

        tags = tags_regular.findall(post.comment)
        if len(tags) < __min_tags_per_post:
            return
        
        #self._logger.debug(f'Try to save {post.photo_url}')
        try:
            urllib.request.urlretrieve(post.photo_url, os.path.join(folder, str(post.id)+'.jpg'))
            return {'id': post.id, 'comment': post.comment, 'tags' : tags, 'accessibility_caption' : post.accessibility_caption}
        except Exception as e:
            #self._logger.error(e)
            return None

    @staticmethod
    def __save_meta(index, __meta_file_path:str, __requested_users, __posts ):
        #self._logger.debug(f"Save... Index {index} Posts {len(self.__posts)} users {len(self.__requested_users)}")
        with open(__meta_file_path, 'w') as file:
            json.dump({'meta': {'last_index': index, 'users': __requested_users, 'posts_count' : len(__posts)}, 'data': __posts},
                    file,
                    indent=4)
    def __try_to_restore(self):
        self._logger.debug("Try to restore data...")
       
        if not os.path.exists(self.__meta_file_path):
            return 0
        with open(self.__meta_file_path, 'r') as file:
            data                    = json.load(file)
        self.__requested_users  = data['meta']['users']
        self.__posts            = data['data']
        index                   = data['meta']['last_index']

        self._logger.info(f"Found cached meta data... Posts {len(self.__posts)} Users {len(self.__requested_users)} Index {index}")

        return index+1


# python .\greedy_parser.py --total_count_of_posts 500 timatiofficial

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('root_user')
    parser.add_argument('--folder', type=str, required=False, default=os.path.join(parent_dir, 'dataset'))
    parser.add_argument('--posts_per_profile', type=int, required=False, default=200)
    parser.add_argument('--following_per_profile', type=int, required=False, default=100)
    parser.add_argument('--total_count_of_posts', type=int, required=False, default=500)
    parser.add_argument('--min_tags_per_post', type=int, required=False, default=3)
    args = parser.parse_args(sys.argv[1:])

    # global_config.logging_level = logging.DEBUG
    # global_config.kill_browser_after_end = False
    parser = GreedyParser(args.root_user, 
                          count_of_posts_per_profile=args.posts_per_profile, 
                          count_of_following_per_profile=args.following_per_profile,
                          total_count_of_posts=args.total_count_of_posts,
                          min_tags_per_post=args.min_tags_per_post)
