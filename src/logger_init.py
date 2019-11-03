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

    rsConfig = logger_configs['radiosonde']

    logFile = os.path.join(
        projectDir, 'log', rsConfig['LOG_FILE'])
    logger = logging.getLogger(__name__)

    fh = logging.FileHandler(logFile)
    fh.setLevel(logModeDict[rsConfig['LOG_MODE_FH']])
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logModeDict[rsConfig['LOG_MODE_CH']])

    formatterFh = logging.Formatter(rsConfig['FORMATTER_FH'])
    formatterCh = logging.Formatter(rsConfig['FORMATTER_CH'])
    fh.setFormatter(formatterFh)
    ch.setFormatter(formatterCh)

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.setLevel(logModeDict['DEBUG'])

    return logger
