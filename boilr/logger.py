import boilr.config as config
import boilr.helpers as helpers

#import sys
import logging

logger = logging.getLogger() #__name__ # doesn't work with handler
date_fmt = '%Y-%m-%dT%H:%M:%S'

file_handler = logging.FileHandler(config.logpath)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(fmt='[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s', datefmt=date_fmt, style='%')
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler() #sys.stdout
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter(fmt='[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s', datefmt=date_fmt, style='%') #'%(levelname)s -- %(message)s'
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler) # log to file
if helpers.is_docker():
    logger.addHandler(console_handler) # log to console

logger.debug("Logging config applied")
