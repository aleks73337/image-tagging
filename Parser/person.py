from browser import Browser
from base import Base
import json

class RequestableContent:
    def __init__(self, page_info : dict):
        self.update(page_info)

    def update(self, page_info : dict):
        self.__page_info = page_info

    def is_can_load_more(self):
        return bool(self.__page_info['has_next_page'])

class Post:
    def __init__(self, post : dict):
        self.photo_url = post['display_url']
        self.accessibility_caption = post['accessibility_caption']
        self.comment = post['edge_media_to_caption']['edges'][0]['node']['text'] # can be more than one??
        # tagged users  ??

    def __str__(self):
        return f"Post {self.comment} accessibility {self.accessibility_caption}"

class Posts(RequestableContent):
    def __init__(self, posts: dict):
        super().__init__(posts['page_info'])
        self.posts = []
        for post in posts['edges']:
            self.posts.append(Post(post['node']))
            
    def __str__(self):
        return str(self.posts)
        

class Person(Base):
    def __init__(self, login : str, browser : Browser):
        super().__init__("Person")
        self.login = login
        self.__browser = browser

        self.__request_base_info()

    def __request_base_info(self):
        response = self.__browser.request(f"https://www.instagram.com/{self.login}/?__a=1")
        self._logger.debug(f"Status code {response.status_code}")
        if response.status_code != 200:
            raise Exception(f"Invalid status code = {response.status_code}")
        
        dict = json.loads(response.text)
        user_json = dict['graphql']['user']

        self.id              = user_json['id']
        self.is_private      = user_json['is_private']
        self.biography       = user_json['biography']
        self.full_name       = user_json['full_name']
        self.people_category = user_json['category_name']
        self.followers_count = user_json['edge_followed_by']['count']
        self.following_count = user_json['edge_follow']['count']
        self.posts           = Posts(user_json['edge_owner_to_timeline_media'])

    def __str__(self):
        return f'Person id {self.id} name {self.full_name} followers {self.followers_count} following {self.following_count}'