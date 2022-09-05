import os
from .utils import *

# Default config
config_dir = os.path.dirname(os.path.abspath(__file__))
config_file = 'config.json'
__default_config__ = os.path.join(config_dir, config_file)

# openCV window name
__window_name__ = 'Hamoco (preview)'
