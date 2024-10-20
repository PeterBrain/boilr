"""Main module"""
import logging

import boilr.logger as logg
import boilr.argparse as argparse


def main():
    """Entry point"""
    args = argparse.parser.parse_args()

    logg.setup_logging(args)

    logger = logging.getLogger(__name__)

    if hasattr(args, 'callback'):
        logger.debug("Executing command callback: %s", args.callback)
        args.callback(args)
    else:
        logger.debug("No callback found, printing help")
        argparse.parser.print_help()


if __name__ == '__main__':
    main()
