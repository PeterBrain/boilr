import sys
import logging
import logging.handlers

import boilr.config as config

logger = logging.getLogger() # root logger
logger.setLevel(logging.DEBUG) # root logging level

file_handler = logging.handlers.TimedRotatingFileHandler(config.SystemConfig.logpath, when='W0', interval=1, backupCount=12)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(fmt=config.SystemConfig.logging_format, datefmt=config.SystemConfig.logging_date_format, style='%')
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.ERROR)
console_formatter = logging.Formatter(fmt=config.SystemConfig.logging_format, datefmt=config.SystemConfig.logging_date_format, style='%')
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler) # log to file
logger.addHandler(console_handler) # log to console

logger.debug("Logging config applied")
