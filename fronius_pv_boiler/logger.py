import fronius_pv_boiler.config as config

import logging
from logging.handlers import RotatingFileHandler

#file_formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s - %(message)s - [in %(pathname)s:%(lineno)d]',"%Y-%m-%dT%H:%M:%S")
#file_handler = RotatingFileHandler(config.logfile, maxBytes=1048576, backupCount=5) # doesn't work with daemon
file_handler = logging.FileHandler(config.logfile)
file_handler.setLevel(logging.INFO)
#file_handler.setFormatter(file_formatter)

console_formatter = logging.Formatter('%(levelname)s -- %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(console_formatter)

#logger = logging.getLogger(__name__)
#logger.addHandler(file_handler)
#logger.addHandler(console_handler)
#logger.setLevel(logging.INFO)

logging.basicConfig(
        handlers=[
                file_handler,
                console_handler
            ],
        #filename='/var/log/fronius_pv_boiler/boilr.log',
        #filemode='a', # 'w'
        level=logging.INFO, # DEBUG, INFO, WARNING, ERROR, CRITICAL
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
