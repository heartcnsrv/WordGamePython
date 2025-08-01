import configparser
import os
import sys
import CORBA
import CosNaming

# These two are your generated stubs
from meowstery.python_client.idl import GameService_idl, UserService_idl


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


def resolve_available_services():
    load_orb_config()

    orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)
    obj = orb.resolve_initial_references("NameService")
    naming_context = obj._narrow(CosNaming.NamingContext)

    def get_service(name, helper_class):
        name_path = [CosNaming.NameComponent(name, "")]
        obj_ref = naming_context.resolve(name_path)
        return obj_ref._narrow(helper_class)

    services = {
        'login': get_service("LoginService", UserService_idl.LoginService),
        'game': get_service("GameService", GameService_idl.GameService),
    }

    return services
