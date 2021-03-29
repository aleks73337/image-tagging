# Insta-parser

## How to use:
1) Place credentials.json to this folder with login and password:
```json
{
    "login": "login@mail.ru",
    "password": "password"
}
```
2) Import parser to your file
```python
from Parser import *
```
This import provides:
- `global_config` with several configs for parsing/logging and etc
- `Parser` - main object to start parsing session
- `Person`, `Post`, `Posts` - objects, that represen objects from Instagram with collected data and functions to collect more data\
  
3) Use =)
```python
parser = Parser()
person = parser.request_person('timatiofficial')
person.posts.request_more(30)

assert person.login == 'timatiofficial'
assert person.id == 189003872
assert person.is_private == False
assert person.posts.id == 189003872
assert len(person.posts.posts) != 0

for post in person.posts.posts:
    assert post.photo_url is not None
    print(post.comment)

person.follow.request_more(20)

assert len(person.follow.followings) != 0
for user_name in person.follow.followings:
    assert user_name is not None
    print(user_name)
```