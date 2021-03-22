from time import sleep
from base import Base
from config import global_config
from browser import Browser
from person import Person

import json

def get_login_password():
    dict = json.load(open('credentials.json', 'r'))
    return dict['login'], dict['password']

class RequestsSession(Base):
    def __init__(self):
        super().__init__("RequestsSession")

        self.__browser = Browser()

        if not self._is_logged_in():
            self._logger.warning("Current session is not logged in...")
            self._log_in()
            if not self._is_logged_in():
                self._logger.error("Current session is not logged in!")
                raise Exception("Cant login in Instagram!")

            self._skip_notifications_if_needed()

    def _is_logged_in(self):
        return self.__browser.open_page('https://www.instagram.com/').find_by_css("input[name='username']") is None

    def _log_in(self):
        self._logger.debug("Try to log in...")

        username, password = get_login_password()
        
        self.__browser.find_by_css("input[name='username']").send_keys(username)
        self.__browser.find_by_css("input[name='password']").send_keys(password)
        self.__browser.find_by_xpath("//button[@type='submit']").click()

        save_button = self.__browser.find_by_xpath("//button[text()[contains(.,'Сохранить данные')]]")
        if save_button:
            save_button.click()

    def _skip_notifications_if_needed(self):
        sleep(3)
        self._logger.debug("Skip notifications if needed")
        save_button = self.__browser.find_by_xpath("//button[text()[contains(.,'Не сейчас')]]")
        if save_button:
            save_button.click()
        else:
            self._logger.debug("No button to skip notifications")
    
    def request_person(self, login : str):
        return Person(login, self.__browser)
