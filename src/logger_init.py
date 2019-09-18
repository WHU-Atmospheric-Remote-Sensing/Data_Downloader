import os
import sys
import logging
from configs import load_logger_config

logger_configs = load_logger_config()
logModeDict = {
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'DEBUG': logging.DEBUG,
    'ERROR': logging.ERROR
    }
projectDir = os.path.dirname(__file__)

# check the folder for saving log files
logDir = os.path.join(projectDir, 'log')
if not os.path.exists(logDir):
    os.mkdir(logDir)

def radiosonde_logger_init():
    """
    initialize the logger for processing radiosonde data.
    """

    logFile = os.path.join(projectDir, logger_configs['radiosonde']['LOG_FILE'])
    logger = logging.getLogger(__name__)
    logger.setLevel(logModeDict[logger_configs['LOG_MODE']])

    logFile = os.path.join(logDir, logger_configs['LOG_FILE'])
    fh = logging.FileHandler(logFile)
    fh.setLevel(logModeDict[logger_configs['LOG_MODE_FH']])
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logModeDict[logger_configs['LOG_MODE_CH']])

    formatterFh = logging.Formatter(logger_configs['FORMATTER_FH'])
    formatterCh = logging.Formatter(logger_configs['FORMATTER_CH'])
    fh.setFormatter(formatterFh)
    ch.setFormatter(formatterCh)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger