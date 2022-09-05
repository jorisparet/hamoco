import os

# Default config
config_dir = os.path.dirname(os.path.abspath(__file__))
config_file = 'nt.json' if os.name == 'nt' else 'posix.json'
__default_config__ = os.path.join(config_dir, config_file)
