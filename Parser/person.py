from typing import List
from .browser import Browser
from .base import Base
from .config import global_config
from abc import ABCMeta, abstractmethod

import json
import emoji

instagram_url = 'https://www.instagram.com'
base_query_url = f'{instagram_url}/graphql/query'


class RequestableContent(Base):
    __metaclass__ = ABCMeta

    def __init__(self, class_name : str, column_inside_user : str, browser : Browser, page_info: dict):
        super().__init__(class_name)

        self.__column_inside_user = column_inside_user
        self.__browser = browser
        self.__page_info = page_info

    def request_more(self, count : int):
        """Requests more posts or followings for current user
       
        Returns:
            list: List of new posts or followings. These posts also added to list
        """
        self._logger.debug(f"Request more {count}")

        if count > 100:
            result = []
            while count > 100:
                result += self.request_more(100)
                count -= 100
            return result + self.request_more(count)

        if not self.__page_info['has_next_page']:
            return []

        response = self.__browser.request(self._generate_request_string(count))

        if response.status_code != 200:
            raise Exception(f"Invalid status code = {response.status_code}")

        dict_data = json.loads(response.text)['data']['user'][self.__column_inside_user]

        self.__page_info = dict_data['page_info']

        return self._process_data(dict_data)

    @abstractmethod
    def _generate_request_string(self, count):
        raise NotImplementedError("Must be overriden")

    @abstractmethod
    def _process_data(self, data : dict):
        raise NotImplementedError("Must be overriden")

    @property
    def end_cursor(self):
        return self.__page_info['end_cursor']


class Post:
    """Class represents access to specific post"""
    def __init__(self, post: dict):
        self.id                     = post['id']
        self.photo_url              = post['display_url']
        self.is_video               = post['is_video']
        self.accessibility_caption  = str(post['accessibility_caption'] if 'accessibility_caption' in post else "")
        self.comment                = str(post['edge_media_to_caption']['edges'][0]['node']['text'] if len(post['edge_media_to_caption']['edges']) >= 1 else "")
        self.comment                = emoji.get_emoji_regexp().sub(r'',self.comment)

        if self.accessibility_caption:
            text= 'May be '
            index = self.accessibility_caption.find(text)
            if index != -1:
                self.accessibility_caption = self.accessibility_caption[index+len(text):]
    def __str__(self):
        return f"Post {self.comment} accessibility {self.accessibility_caption}"


class Posts(RequestableContent):
    """Class represents access to posts of specific person"""
    def __init__(self, id: int, browser: Browser, in_posts: dict):
        RequestableContent.__init__(self, "Posts", "edge_owner_to_timeline_media", browser, in_posts['page_info'])

        self.id = id
        self.__posts = self.__process_posts(in_posts['edges'])

        # hard code, probably i will need obtain it in dynamic
        self.hash = '003056d32c2554def87228bc3fd9668a'

    def __process_posts(self, in_posts):
        #self._logger.debug(in_posts)
        return [Post(post['node']) for post in in_posts]

    @property
    def data(self):
        return self.__posts

    def _process_data(self, data: dict):
        new_posts = self.__process_posts(data['edges'])
        self.__posts += new_posts
        return new_posts

    def _generate_request_string(self, count):
        variables = f'{{"id":"{self.id}","first":{count},"after":"{self.end_cursor}"}}'
        request = f'{base_query_url}/?query_hash={self.hash}&variables={variables}'
        self._logger.debug(f'Do request = {request}')
        return request

class Follow(RequestableContent):
    def __init__(self, id : int, browser : Browser, count : int):
        RequestableContent.__init__(self, "Follow", "edge_follow", browser, {'has_next_page': True, 'end_cursor' : None})
        self.id = id
        self.max_count = count
        self.hash = '3dec7e2c57367ef3da3d987d89f9dbc8'
        self.__followings = []

    @property
    def data(self) -> List[str]:
        """Returns list of usernames"""
        return self.__followings

    def _process_data(self, data: dict):
        new_followings = [edge['node']['username'] for edge in data['edges'] if not edge['node']['is_private']]
        self.__followings += new_followings
        return new_followings

    def _generate_request_string(self, count):
        after = f',"after" :"{self.end_cursor}"' if self.end_cursor else ''
        variables = f'{{"id":"{self.id}", "include_reel":false, "fetch_mutual":false, "first":{count}{after}}}'
        request = f'{base_query_url}/?query_hash={self.hash}&variables={variables}'
        self._logger.debug(f'Do request = {request}')
        return request

class Person(Base):
    def __init__(self, login: str, browser: Browser):
        super().__init__("Person")
        self.login = login
        self.__browser = browser

        self.__request_base_info()

    def __request_base_info(self):
        self._logger.debug(f"Request base info for {self.login}")
        response = self.__browser.request(f"{instagram_url}/{self.login}/?__a=1")

        self._logger.debug(f"Status code {response.status_code}")
        if response.status_code != 200:
            raise Exception(f"Invalid status code = {response.status_code}")

        dict = json.loads(response.text)
        try:
            user_json = dict['graphql']['user']
        except:
            self._logger.exception(f'Dict : {dict} login {self.login}')
            raise

        self.id = int(user_json['id'])
        self.is_business_account = user_json['is_business_account']
        self.is_private = user_json['is_private']
        self.biography = user_json['biography']
        self.full_name = user_json['full_name']
        self.people_category = user_json['category_name']
        self.followers_count = user_json['edge_followed_by']['count']
        self.following_count = user_json['edge_follow']['count']

        self.posts = Posts(self.id,
                           self.__browser,
                           user_json['edge_owner_to_timeline_media'])

        self.follow = Follow(self.id, self.__browser, self.followers_count)

    def __str__(self):
        return f'Person id {self.id} name {self.full_name} followers {self.followers_count} following {self.following_count}'
