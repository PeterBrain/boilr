"""Logger module"""
import os
import sys
import logging
import logging.handlers

import boilr.config as config

file_handler = None
console_handler = None


def setup_logging(args):
    """Setup logging config with handler"""
    # pylint: disable=global-statement
    global file_handler, console_handler

    logger = logging.getLogger()  # root logger
    logger.setLevel(logging.DEBUG)  # root logging level

    try:
        log_dir = os.path.dirname(config.SystemConfig.logpath)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            sys.stderr.write(f"Created log directory: {log_dir}\n")

        # Timed rotating file handler
        file_handler = logging.handlers.TimedRotatingFileHandler(
            config.SystemConfig.logpath,
            when='W0',  # rotate weekly
            interval=1,
            backupCount=12
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            fmt=config.SystemConfig.logging_format,
            datefmt=config.SystemConfig.logging_date_format,
            style='%'
        )
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.ERROR)
        console_formatter = logging.Formatter(
            fmt=config.SystemConfig.logging_format,
            datefmt=config.SystemConfig.logging_date_format,
            style='%'
        )
        console_handler.setFormatter(console_formatter)

        # Add handlers to the root logger
        logger.addHandler(file_handler)  # log to file
        logger.addHandler(console_handler)  # log to console

    except PermissionError as e_permission:
        sys.stderr.write(f"PermissionError: {e_permission}\n")
        sys.exit(1)

    except Exception as e_general:
        sys.stderr.write(f"Logging setup failed: {e_general}\n")
        sys.exit(1)

    else:
        if args.verbose:
            file_handler.setLevel(logging.DEBUG)
            console_handler.setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            logger.debug("Verbose mode enabled")

        logger.debug("Logging configuration successfully applied")
