import logging
from requests_session import RequestsSession
from config import global_config
from base import Base
import json


class Parser(Base):
    def __init__(self):
        super().__init__("Parser")
        self.__browser = RequestsSession()
        print(json.loads(self.__browser.request("https://www.instagram.com/durov/?__a=1").text))


if __name__ == '__main__':
    global_config.logging_level = logging.DEBUG
    parser = Parser()
