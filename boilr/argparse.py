"""Parse arguments module"""
import argparse
import sys

import boilr.config as config
import boilr.daemon as daemon


class CustomArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser to override default error handling"""
    def error(self, message):
        """Custom error handler"""
        sys.stderr.write(f"Error: {message}\n")
        sys.stderr.write("Use boilr -h to show further instructions\n")
        sys.exit(2)


def setup_parser():
    """Setup the argument parser with subcommands and options"""
    custom_parser = CustomArgumentParser(
        prog=config.SystemConfig.prog_name,
        description='Water boiler automation with a Fronius pv inverter on a Raspberry Pi.',
        epilog='Additional hardware required. Please check: https://github.com/PeterBrain/boilr',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    custom_parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='increase verbosity',  # (default: %(default)s)
        required=False
    )

    subparsers = custom_parser.add_subparsers(
        title='commands',
        dest='command',
        description='Choose between the following positional arguments',
        help=""
    )

    sp_start = subparsers.add_parser(name='start', help='Start %(prog)s service')
    sp_stop = subparsers.add_parser(name='stop', help='Stop %(prog)s service')
    sp_status = subparsers.add_parser(name='status', help='Show the status of %(prog)s service')
    sp_restart = subparsers.add_parser(name='restart', help='Restart %(prog)s service')
    sp_run = subparsers.add_parser(name='run', help='Start %(prog)s in command-line')
    sp_manual = subparsers.add_parser(name='manual', help='Manually override contactor')

    sp_manual.add_argument(
        'manual',
        nargs=1,
        type=int,
        choices={0, 1},
        help='Manual override contactor (0 = inactive; 1 = active)'
    )

    sp_stop.set_defaults(callback=daemon.daemon_stop)
    sp_status.set_defaults(callback=daemon.daemon_status)
    sp_start.set_defaults(callback=daemon.daemon_start)
    sp_restart.set_defaults(callback=daemon.daemon_restart)
    sp_run.set_defaults(callback=daemon.daemon_run)
    sp_manual.set_defaults(callback=daemon.daemon_manual)

    return custom_parser


parser = setup_parser()
