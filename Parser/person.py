from browser import Browser
from base import Base
from config import global_config

import json

instagram_url = 'https://www.instagram.com'
base_query_url = f'{instagram_url}/graphql/query'


class RequestableContent:
    def __init__(self, page_info: dict):
        self.update(page_info)

    def update(self, page_info: dict):
        self.__page_info = page_info

    @property
    def end_cursor(self):
        return self.__page_info['end_cursor']

    def is_can_load_more(self):
        return bool(self.__page_info['has_next_page'])


class Post:
    """Class represents access to specific post"""
    def __init__(self, post: dict):
        self.photo_url = post['display_url']
        self.accessibility_caption = post['accessibility_caption']
        # can be more than one??
        self.comment = post['edge_media_to_caption']['edges'][0]['node']['text']
        # tagged users  ??

    def __str__(self):
        return f"Post {self.comment} accessibility {self.accessibility_caption}"


class Posts(RequestableContent, Base):
    """Class represents access to posts of specific person"""
    def __init__(self, id: int, browser: Browser, posts: dict):
        RequestableContent.__init__(self, posts['page_info'])
        Base.__init__(self, 'Posts')

        self.id = id
        self.__browser = browser
        self.__posts = [Post(post['node']) for post in posts['edges'] if 'accessibility_caption' in post['node']]

        # hard code, probably i will need obtain it in dynamic
        self.hash = '003056d32c2554def87228bc3fd9668a'

    @property
    def posts(self):
        return self.__posts

    def request_more(self, count: int):
        """Requests more posts for current user
        Count of posts to request can't be more than 100. If you need more - call this function several times

        Returns:
            list: List of new posts. These posts also added to self.posts list
        """

        if count > 100:
            raise Exception("Count can be more than 100!")

        if not self.is_can_load_more():
            return []

        response = self.__get_request(count)

        if response.status_code != 200:
            raise Exception(f"Invalid status code = {response.status_code}")

        dict_data = json.loads(response.text)['data']['user']['edge_owner_to_timeline_media']

        super().update(dict_data['page_info'])

        new_posts = [Post(post['node']) for post in dict_data['edges'] if 'accessibility_caption' in post['node']]
        self.__posts += new_posts
        return new_posts

    def __get_request(self, count: int):
        variables = f'{{"id":"{self.id}","first":{count},"after":"{self.end_cursor}"}}'
        request = f'{base_query_url}/?query_hash={self.hash}&variables={variables}'
        self._logger.debug(f'Do request = {request}')

        return self.__browser.request(request)

    def __str__(self):
        return str(self.posts)

class Follow(RequestableContent, Base):
    def __init__(self, id : int, browser : Browser, count : int):
        RequestableContent.__init__(self,{'has_next_page': True, 'end_cursor' : None})
        Base.__init__(self, 'Follow')
        self.id = id
        self.__browser = browser
        self.max_count = count
        self.hash = '3dec7e2c57367ef3da3d987d89f9dbc8'
        self.followings = []

    def request_more(self, count : int):
        """Requests more followings for current user
        Count of followings to request can't be more than 100. If you need more - call this function several times

        Returns:
            list: List of new followings. These followings also added to self.followings list
        """

        if not self.is_can_load_more():
            return []

        if count > 100:
            raise Exception("Count can be more than 100!")

        response = self.__get_request(count)

        if response.status_code != 200:
            raise Exception(f"Invalid status code = {response.status_code}")

        dict_data = json.loads(response.text)['data']['user']['edge_follow']
        super().update(dict_data['page_info'])

        new_followings = [edge['node']['username'] for edge in dict_data['edges'] if not edge['node']['is_private'] ]
        self.followings += new_followings
        return new_followings

    def __get_request(self, count: int):
        after = f',"after" :"{self.end_cursor}"' if self.end_cursor else ''
        variables = f'{{"id":"{self.id}", "include_reel":true, "fetch_mutual":false,"first":{count}{after}}}'
        request = f'{base_query_url}/?query_hash={self.hash}&variables={variables}'

        self._logger.debug(f'Do request = {request}')

        return self.__browser.request(request)


class Person(Base):
    def __init__(self, login: str, browser: Browser):
        super().__init__("Person")
        self.login = login
        self.__browser = browser

        self.__request_base_info()

    def __request_base_info(self):
        response = self.__browser.request(
            f"{instagram_url}/{self.login}/?__a=1")
        self._logger.debug(f"Status code {response.status_code}")
        if response.status_code != 200:
            raise Exception(f"Invalid status code = {response.status_code}")

        dict = json.loads(response.text)
        user_json = dict['graphql']['user']

        self.id = int(user_json['id'])
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
