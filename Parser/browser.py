from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from seleniumrequests import Chrome
from selenium.common.exceptions import NoSuchElementException

from typing import Optional
from .config import global_config
from .base import Base

import os
cur_dir = os.path.dirname(os.path.abspath(__file__))


class Browser(Base):
    def __init__(self):
        super().__init__("Browser")
        self.__browser = self.__init_browser()

    def __del__(self):
        if global_config.kill_browser_after_end:
            self.__browser.close()

    def __init_browser(self):
        self._logger.debug("Init browser")

        options = webdriver.ChromeOptions()

        if not global_config.show_browser_window:
            options.add_argument('--headless')

        options.add_argument(f"user-data-dir={cur_dir}/selenium")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument(
            f'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36')
        browser = Chrome(options=options, executable_path=os.path.join(cur_dir, 'chromedriver.exe'))
        browser.implicitly_wait(5)
        return browser

    def __safe_find_element(self, command: str) -> Optional[WebElement]:
        try:
            self._logger.debug(f"Execute command.. {command}")
            return eval(command)
        except NoSuchElementException:
            self._logger.debug(f"Can't find such an element")
            return None

    def find_by_xpath(self, xpath: str):
        self._logger.debug(f"Try to find {xpath} by xpath...")
        return self.__safe_find_element(f"self._Browser__browser.find_element_by_xpath(\"{xpath}\")")

    def find_by_css(self, selector: str):
        self._logger.debug(f"Try to find {selector} by css selector...")
        return self.__safe_find_element(f"self._Browser__browser.find_element_by_css_selector(\"{selector}\")")

    def open_page(self, url: str):
        self._logger.debug(f"Open page {url}")
        self.__browser.get(url)
        return self

    def request(self, url : str):
        self._logger.debug(f'Request: {url}')
        return self.__browser.request("get", url)