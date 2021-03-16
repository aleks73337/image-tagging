import logging

class Config:
    def __init__(self):
        self.logging_level = logging.INFO
        self.kill_browser_after_end = True
        self.show_browser_window = True

global_config = Config()