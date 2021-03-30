import urllib.request
import os
import sys
import json
import re
import logging

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
                folder_to_save_data            : str = parent_dir+'/dataset'):

        super().__init__("GreedyParser")

        self.__parser               = Parser()
        self.__count_of_posts       = count_of_posts_per_profile
        self.__cont_of_following    = count_of_following_per_profile
        self.__total_count_of_posts = total_count_of_posts
        self.__min_tags_per_post    = min_tags_per_post
        self.__folder               = folder_to_save_data
        self.__meta_file_path       = os.path.join(self.__folder, '_meta.json')

        if not os.path.exists(self.__folder):
            os.makedirs(self.__folder)

        self.__parse(start_user_name)

    def __parse(self, start_user_name : str):
        self.__posts                = []
        self.__requested_users = [start_user_name]

        index = self.__try_to_restore()
        initial_count = len(self.__posts)

        self.__bar = tqdm(total=self.__total_count_of_posts)

        while index < len(self.__requested_users):
            if len(self.__posts) - initial_count >= self.__total_count_of_posts:
                break

            self.__process_user_name(self.__requested_users[index])
            self.__save_meta(index)
            index += 1
        self.__bar.close()

        self._logger.info(f"Collected {len(self.__posts) - initial_count} new post")

    def __process_user_name(self, username : str):
        self._logger.debug(f'Request {username}')
        user = self.__parser.request_person(username)
        self.__bar.set_description(f'Current user is {username}')

        if user.is_business_account or user.is_private:
            return

        for post in _get_data(user.posts, self.__count_of_posts):
            self.__process_post(post)

        for username in _get_data(user.follow, self.__cont_of_following):
            if username not in self.__requested_users:
                self.__requested_users.append(username)

    def __process_post(self, post : Post):
        tags = tags_regular.findall(post.comment)
        if len(tags) < self.__min_tags_per_post:
            return
        
        urllib.request.urlretrieve(post.photo_url, os.path.join(self.__folder, str(post.id)+'.jpg'))
        self.__posts.append({'id': post.id, 'comment': post.comment, 'tags' : tags, 'accessibility_caption' : post.accessibility_caption})
        self.__bar.update(1)

    def __save_meta(self, index):
        self._logger.debug(f"Save... Index {index} Posts {len(self.__posts)} users {len(self.__requested_users)}")
        json.dump({'meta': {'last_index': index, 'users': self.__requested_users, 'posts_count' : len(self.__posts)}, 'data': self.__posts},
                open(self.__meta_file_path, 'w'),
                indent=4)
    def __try_to_restore(self):
        self._logger.debug("Try to restore data...")
       
        if not os.path.exists(self.__meta_file_path):
            return 0
        
        data                    = json.load(open(self.__meta_file_path, 'r'))
        self.__requested_users  = data['meta']['users']
        self.__posts            = data['data']
        index                   = data['meta']['last_index']

        self._logger.info(f"Found cached meta data... Posts {len(self.__posts)} Users {len(self.__requested_users)} Index {index}")

        return index+1


# python .\greedy_parser.py --total_count_of_posts 100 --posts_per_profile 200 --min_tags_per_post 3 timatiofficial

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('root_user')
    parser.add_argument('--folder', type=str, required=False, default=parent_dir+'/dataset')
    parser.add_argument('--posts_per_profile', type=int, required=False, default=100)
    parser.add_argument('--following_per_profile', type=int, required=False, default=100)
    parser.add_argument('--total_count_of_posts', type=int, required=False, default=500)
    parser.add_argument('--min_tags_per_post', type=int, required=False, default=3)
    args = parser.parse_args(sys.argv[1:])

    #global_config.logging_level = logging.DEBUG
    parser = GreedyParser(args.root_user, 
                          count_of_posts_per_profile=args.posts_per_profile, 
                          count_of_following_per_profile=args.following_per_profile,
                          total_count_of_posts=args.total_count_of_posts,
                          min_tags_per_post=args.min_tags_per_post)
