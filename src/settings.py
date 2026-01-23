################################# Settings Module ####################################
#
# This module provides a global, application-wide configuration object.
# It should be initialized once at the start of the application.
#
######################################################################################

import yaml
import sys
import os
import shutil
from pathlib import Path

# This will be the global CONFIG object. It's None until initialized.
CONFIG = None

# Global paths
APP_NAME = "annotes"
USER_DATA_DIR = Path.home() / f".{APP_NAME}"

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)

    return Path(base_path) / relative_path

def initialize():
    """
    Loads the configuration from config.yaml into the global 'CONFIG' variable.
    Ensures a user-writable config file exists.
    """
    global CONFIG
    from utils import load_config

    # Ensure user data directory exists
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    config_path = USER_DATA_DIR / "config.yaml"
    
    # If config doesn't exist in user dir, try to copy from default
    if not config_path.exists():
        print(f"⚠️ No config found at {config_path}. Attempting to create from default...")
        
        default_config_path = get_resource_path("config.default.yaml")
        
        if default_config_path.exists():
            try:
                shutil.copy2(default_config_path, config_path)
                print(f"✅ Created default config at: {config_path}")
            except Exception as e:
                print(f"❌ Failed to create default config: {e}")
        else:
            print(f"❌ Default config not found at resource path: {default_config_path}")

    # Load the config (either existing or newly created)
    CONFIG = load_config(config_path)

    # Fallback: If loading failed (e.g. permission error), try loading default direct from bundle
    if CONFIG is None:
        print("⚠️ Failed to load user config. Falling back to internal defaults (read-only mode).")
        default_config_path = get_resource_path("config.default.yaml")
        CONFIG = load_config(default_config_path)
    
    # --- AUTO-CREATE FOLDERS & EXPAND PATHS ---
    if CONFIG:
        for key in ["pdf_folder", "notes_folder"]:
            path_str = CONFIG.get(key)
            if path_str:
                # Expand ~ if present
                expanded_path = Path(path_str).expanduser()
                CONFIG[key] = str(expanded_path)
                
                # Ensure the folder exists
                if not expanded_path.exists():
                    try:
                        expanded_path.mkdir(parents=True, exist_ok=True)
                        print(f"📁 Created missing {key}: {expanded_path}")
                    except Exception as e:
                        print(f"❌ Could not create {key} at {expanded_path}: {e}")
