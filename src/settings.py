################################# Settings Module ####################################
#
# This module provides a global, application-wide configuration object.
# It should be initialized once at the start of the application.
#
######################################################################################

import yaml
from pathlib import Path

# This will be the global CONFIG object. It's None until initialized.
CONFIG = None


def initialize():
    """Loads the configuration from CONFIG.yaml into the global 'CONFIG' variable."""
    global CONFIG
    config_file_path = Path(__file__).parent / "config.yaml"
    from utils import load_config

    CONFIG = load_config(config_file_path)
