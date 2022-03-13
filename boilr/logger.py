import boilr.config as config
import boilr.helper as helper

import sys
import logging

logger = logging.getLogger() # root logger
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(config.SystemConfig.logpath)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(fmt=config.SystemConfig.logging_format, datefmt=config.SystemConfig.logging_date_format, style='%')
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.ERROR)
console_formatter = logging.Formatter(fmt=config.SystemConfig.logging_format, datefmt=config.SystemConfig.logging_date_format, style='%')
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler) # log to file
#if helper.is_docker():
logger.addHandler(console_handler) # log to console

logger.debug("Logging config applied")
