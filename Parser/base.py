import logging
from .config import global_config

logging.basicConfig()
logging.basicConfig(level=logging.NOTSET)

class Base:
    def __init__(self, name: str):
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(level=global_config.logging_level)
    
    @property
    def _logger(self):
        return self.__logger
