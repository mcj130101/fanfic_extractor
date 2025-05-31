# fanficdownloader/config.py

import os
import sys

# Configuration directory and file setup
def get_config_dir() -> str:
    """Get the appropriate config directory based on the operating system."""
    if sys.platform == 'win32':
        # Windows: Use AppData\Roaming
        config_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'FanFicDownloader')
    elif sys.platform == 'darwin':
        # macOS: Use ~/Library/Application Support
        config_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'FanFicDownloader')
    else:
        # Linux/Unix: Use ~/.config
        config_dir = os.path.join(os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')),
                                  'FanFicDownloader')

    # Create config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

# Global constants for configuration paths
CONFIG_DIR: str = get_config_dir()
CONFIG_FILE: str = os.path.join(CONFIG_DIR, "config.txt")
DEFAULT_DOWNLOAD_FOLDER: str = os.path.join(os.path.expanduser("~"), "FanFicDownloads")

# Global variable to store the user's configured download folder
USER_FOLDER: str = DEFAULT_DOWNLOAD_FOLDER

def load_config() -> str:
    """
    Loads configuration settings from a file and initializes the global USER_FOLDER.
    Returns the loaded download folder path.
    """
    global USER_FOLDER
    try:
        with open(CONFIG_FILE, "r") as file:
            config_lines = file.readlines()
            download_folder = config_lines[0].strip() if len(config_lines) > 0 else DEFAULT_DOWNLOAD_FOLDER
            USER_FOLDER = download_folder
            # Ensure the loaded folder exists
            os.makedirs(USER_FOLDER, exist_ok=True)
            return download_folder
    except FileNotFoundError:
        USER_FOLDER = DEFAULT_DOWNLOAD_FOLDER
        # Ensure the default folder exists if config file isn't found
        os.makedirs(USER_FOLDER, exist_ok=True)
        return DEFAULT_DOWNLOAD_FOLDER
    except Exception:
        # Fallback to default if there's any issue reading the config file
        USER_FOLDER = DEFAULT_DOWNLOAD_FOLDER
        os.makedirs(USER_FOLDER, exist_ok=True)
        return DEFAULT_DOWNLOAD_FOLDER

def save_config(download_folder: str):
    """
    Saves the new download folder location to the config file and updates USER_FOLDER.
    """
    global USER_FOLDER
    with open(CONFIG_FILE, "w") as file:
        file.write(f"{download_folder}\n")
    USER_FOLDER = download_folder # Update the global variable after saving

# Initialize USER_FOLDER when this module is imported
load_config()