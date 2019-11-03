import mysql.connector
from mysql.connector import errorcode
import toml
from configs import load_database_config
from logger_init import radiosonde_logger_init

DATABASE_CONFIG = load_database_config()
USER = DATABASE_CONFIG['login_credential']
logger = radiosonde_logger_init()

class RadiosondeDB(object):
    """
    """

    def __init__(self):
        
        self.conn = mysql.connector(
            host=DATABASE_CONFIG[USER]['DATABASE_HOST'],
            user=DATABASE_CONFIG[USER]['DATABASE_USERNAME'],
            password=DATABASE_CONFIG[USER]['DATABASE_PASSWORD'],
            database=DATABASE_CONFIG[USER]['DATABASE_NAME'],
            port=DATABASE_CONFIG[USER]['DATABASE_PORT'],
            raise_on_warnings=True
        )

    # create tables

    # insert entry

    # delete entry

    # search entry