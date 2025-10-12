"""Main module"""
import logging

from boilr.context import Context
import boilr.config as config
import boilr.argparse as argparse
import boilr.logger as logg
import boilr.core as core
import boilr.app as app


def main():
    """Entry point"""
    logg.setup_bootstrap_logging()

    # CLI argument parsing
    parser = argparse.get_parser()
    args = parser.parse_args()

    # Load configuration
    cfg = config.initialize(args)
    ctx = Context(args=args, config=cfg, logger=logging.getLogger(__name__))

    # Full logging
    logg.setup_logging(ctx)
    logger = logging.getLogger(__name__)

    # Instantiate main control objects
    ctx.main_ctrl = core.MainCtrl(ctx)
    ctx.boilr = app.Boilr(ctx)

    if hasattr(args, 'verbose') and getattr(args, 'verbose'):
        ctx.main_ctrl.verbose = args.verbose
        ctx.console_handler.setLevel(logging.DEBUG)

    # Execute the command callback if exists
    if hasattr(args, "callback") and callable(args.callback):
        logger.debug("Executing command callback: %s", args.callback)
        args.callback(ctx)
    else:
        logger.debug("No callback found, printing help")
        parser.print_help()


if __name__ == "__main__":
    main()
