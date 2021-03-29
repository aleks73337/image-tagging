import urllib.request
import os
import sys
import json
import re

from tqdm import tqdm

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from Parser.base import Base
from Parser.insta_parser import Parser
from Parser.config import global_config



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

        if not os.path.exists(self.__folder):
            os.makedirs(self.__folder)

        self.__parse(start_user_name)

    def __parse(self, start_user_name : str):
        requested_users = [start_user_name]
        posts = []

        index = 0
        bar = tqdm(total=self.__total_count_of_posts)
        tags_regular = re.compile(r'#\w+')
        while len(posts) < self.__total_count_of_posts and index < len(requested_users):
            #print(f'Progress: {len(posts)}/{self.__total_count_of_posts}')
            self._logger.debug(f'Request {requested_users[index]}')
            user = self.__parser.request_person(requested_users[index])
            index += 1

            count_of_posts = len(user.posts.posts)
            self._logger.debug(f'Count of posts {count_of_posts}')

            if count_of_posts < self.__count_of_posts:
                user.posts.request_more(self.__count_of_posts - count_of_posts)

            for post in user.posts.posts[:self.__count_of_posts]:
                tags = tags_regular.findall(post.comment)
                if len(tags) < self.__min_tags_per_post:
                    continue
                
                urllib.request.urlretrieve(post.photo_url, os.path.join(self.__folder, str(post.id)+'.jpg'))
                posts.append({'id': post.id, 'comment': post.comment, 'tags' : tags, 'accessibility_caption' : post.accessibility_caption})
                bar.update(1)

            count_of_users = len(user.follow.followings)
            self._logger.debug(f'Count of users {count_of_users}')
            
            if count_of_users < self.__cont_of_following:
                user.follow.request_more(self.__cont_of_following - count_of_users)

            for username in user.follow.followings[:self.__cont_of_following]:
                if username not in requested_users:
                    requested_users.append(username)

        json.dump(posts, open(os.path.join(self.__folder, 'meta.json'), 'w'), indent=4)
        bar.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('root_user')
    parser.add_argument('--folder', type=str, required=False, default=parent_dir+'/dataset')
    args = parser.parse_args(sys.argv[1:])


    #global_config.logging_level = logging.DEBUG
    parser = GreedyParser(args.root_user, 10, 10, 50)