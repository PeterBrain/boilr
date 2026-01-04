"""Logger module"""
import os
import sys
import logging
import logging.handlers


def setup_bootstrap_logging():
    """Setup minimal logger to stderr for early startup"""
    root = logging.getLogger()
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    root.debug("Bootstrap logging initialized")


def setup_logging(ctx):
    """Setup logging config with handler"""
    logger = logging.getLogger()  # root logger
    logger.setLevel(logging.DEBUG)  # root log level

    # Remove any existing handlers
    for h in logger.handlers[:]:
        logger.removeHandler(h)

    try:
        log_dir = os.path.dirname(ctx.config.system.logpath)
        # os.makedirs(log_dir, exist_ok=True)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            sys.stderr.write(f"Created log directory: {log_dir}\n")

        # Timed rotating file handler
        file_handler = logging.handlers.TimedRotatingFileHandler(
            ctx.config.system.logpath,
            when="W0",  # rotate weekly
            interval=1,
            backupCount=12
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            fmt=ctx.config.system.logging_format,
            datefmt=ctx.config.system.logging_date_format,
            style="%"
        )
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter(
            fmt=ctx.config.system.logging_format,
            datefmt=ctx.config.system.logging_date_format,
            style="%"
        )
        console_handler.setFormatter(console_formatter)

        # Add handlers to the root logger
        logger.addHandler(file_handler)  # log to file
        logger.addHandler(console_handler)  # log to console

        ctx.logger = logger
        ctx.file_handler = file_handler
        ctx.console_handler = console_handler

        if getattr(ctx.args, "verbose", False) or ctx.config.system.log_level.upper() == "DEBUG":
            for h in logger.handlers:
                h.setLevel(logging.DEBUG)

            logger.setLevel(logging.DEBUG)
            logger.debug("Verbose mode enabled")

        else:
            log_level = ctx.config.system.log_level.upper()
            numeric_level = getattr(logging, log_level, logging.WARNING)
            logger.setLevel(numeric_level)

            for h in logger.handlers:
                h.setLevel(numeric_level)

        logger.debug("Logging configuration applied")

    except PermissionError as e_permission:
        sys.stderr.write(f"PermissionError: {e_permission}\n")
        sys.exit(1)

    except Exception as e_general:
        sys.stderr.write(f"Logging setup failed: {e_general}\n")
        sys.exit(1)
