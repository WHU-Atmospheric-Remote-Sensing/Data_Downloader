import os
import toml

CONFIG_DIR = os.path.join(os.path.dirname(os.getcwd()), 'config')
METADATA_DIR = os.path.join(os.path.dirname(os.getcwd()), 'config', 'metadata')
DOWNLOAD_CONFIG_FILE = "download_config.toml"
DATABASE_CONFIG_FILE = "database_config.toml"
LOGGER_CONFIG_FILE = "logger_config.toml"
RADIOSONDE_METADATA_FILE = "radiosonde_metadata.toml"

def load_download_config():
    """
    load the configurations related with the download operations
    """

    download_config_path = os.path.join(CONFIG_DIR, DOWNLOAD_CONFIG_FILE)
    with open(download_config_path, 'r', encoding='utf-8') as fh:
        configs = toml.loads(fh.read())

    return configs


def load_database_config():
    """
    load the configurations related with the database
    """

    database_config_path = os.path.join(CONFIG_DIR, DATABASE_CONFIG_FILE)
    with open(database_config_path, 'r', encoding="utf-8") as fh:
        configs = toml.loads(fh.read())

    return configs


def load_logger_config():
    """
    load the configurations related with the logger
    """

    logger_config_path = os.path.join(CONFIG_DIR, LOGGER_CONFIG_FILE)
    with open(logger_config_path, 'r', encoding="utf-8") as fh:
        configs = toml.loads(fh.read())

    return configs


def load_radiosonde_metadata():
    """
    load the configurations for radiosonde metadata.
    """

    rs_metadata_path = os.path.join(METADATA_DIR, RADIOSONDE_METADATA_FILE)
    with open(rs_metadata_path, 'r', encoding='utf-8') as fh:
        configs = toml.loads(fh.read())

    return configs