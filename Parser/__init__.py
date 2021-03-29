import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .config import global_config
from .insta_parser import Parser
from .person import Person, Post, Posts


