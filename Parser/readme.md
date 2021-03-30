# Insta-parser

## How to use:
1) Place credentials.json to this folder with login and password:
```json
{
    "login": "login@mail.ru",
    "password": "password"
}
```

### By yourself:
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
assert len(person.posts.data) != 0

for post in person.posts.data:
    assert post.photo_url is not None
    print(post.comment)

person.follow.request_more(20)

assert len(person.follow.data) != 0
for user_name in person.follow.data:
    assert user_name is not None
    print(user_name)
```
### Use greedy-parser
2) Run greedy-parser with arguments
   1) `--folder` - folder to save dataset
   2) `--posts_per_profile` - count of posts per profile, that parser should to load. It is only loading, not adding. for example, all of these posts can be without hashtag, so they will be ignored
   3) `--following_per_profile` - same as before, but only for followings
   4) `--total_count_of_posts` - min count of posts you expect to got. Only min, due to parser stops only after processing specific profile
   5) `--min_tags_per_post` 
   6) `root_user` - main argument. Username to start parsing

dataset collection is cacheable. It means, that if you run parser with same folder, it start from the point, where it finished last time (from last visited profile +1)


## Known issues
Sometimes it is possible to see, that browser get stucked at the start with attemtion to load some local address.... in this case, please, restart session.

### Changelist:
- Greedy-parsr caches its state to continue on next run
- Now greedy-parser avoids business accounts