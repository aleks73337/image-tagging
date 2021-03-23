from requests_session import RequestsSession
from base import Base


class Parser(Base):
    def __init__(self):
        super().__init__("Parser")
        self.__browser = RequestsSession()

    def request_person(self, url : str):
        return self.__browser.request_person(url)