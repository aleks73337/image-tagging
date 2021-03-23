from config import global_config
from insta_parser import Parser
import logging

global_config.logging_level = logging.DEBUG

def test_load_timaty():
    parser = Parser()
    person = parser.request_person('timatiofficial')
    person.posts.request_more(30)

    assert person.login == 'timatiofficial'
    assert person.id == 189003872
    assert person.is_private == False
    assert person.posts.id == 189003872

    for post in person.posts.posts:
        assert post.photo_url is not None
        print(post.comment)

    person.follow.request_more(20)
    for user_name in person.follow.followings:
        assert user_name is not None
        print(user_name)