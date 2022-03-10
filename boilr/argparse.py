import boilr.config as config
import boilr.daemon as daemon

import argparse

parser = argparse.ArgumentParser(
        prog=config.SystemConfig.prog_name,
        description='Water boiler automation with a Fronius pv inverter on a Raspberry Pi.',
        epilog='Additional hardware required. Please check: https://github.com/PeterBrain/boilr'
    )

subparsers = parser.add_subparsers(title='commands') #description='valid commands' #help='additional help'
sp_start = subparsers.add_parser(name='start', help='Starts %(prog)s daemon')
sp_stop = subparsers.add_parser(name='stop', help='Stops %(prog)s daemon')
sp_status = subparsers.add_parser(name='status', help='Show the status of %(prog)s daemon')
sp_restart = subparsers.add_parser(name='restart', help='Restarts %(prog)s daemon')
sp_debug = subparsers.add_parser(name='debug', help='Starts %(prog)s daemon in debug mode')
sp_manual = subparsers.add_parser(name='manual', help='Manually override gpio channel (contactor)')

args_group = parser#.add_argument_group('default', 'description')
args_group.add_argument('-v', '--verbose', action='store_true', help='log extra information', required=False)
sp_manual.add_argument('manual', nargs=1, type=int, choices={0,1}, help='Manual override (0 = inactive; 1 = active)')

sp_stop.set_defaults(callback=daemon.daemon_stop)
sp_status.set_defaults(callback=daemon.daemon_status)
sp_start.set_defaults(callback=daemon.daemon_start)
sp_restart.set_defaults(callback=daemon.daemon_restart)
sp_debug.set_defaults(callback=daemon.daemon_debug)
sp_manual.set_defaults(callback=daemon.daemon_manual)

args = parser.parse_args()

if hasattr(args, 'callback'):
    args.callback(args)
else:
    parser.print_help()
    #parser.print_usage()
