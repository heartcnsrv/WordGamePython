import configparser
import os

from future.moves import sys


def load_orb_config(config_path=None):
    config = configparser.ConfigParser()

    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    config.read(config_path)

    try:
        host = config['ORB']['host']
        port = config['ORB']['port']

        name_service_ref = f"NameService=corbaloc::{host}:{port}/NameService"
        if "-ORBInitRef" not in sys.argv:
            sys.argv.extend(["-ORBInitRef", name_service_ref])

        return host, port
    except KeyError as e:
        raise KeyError(f"Missing key in config file: {e}")