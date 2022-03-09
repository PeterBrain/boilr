import boilr.logger as logg
import boilr.config as config
import boilr.core_app as core_app
import boilr.rpi_gpio as rpi_gpio

import sys, os
import time
import logging
import argparse
import signal
import daemon
from daemon import pidfile

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MainCtrl:
    def __init__(self, thread_continue=None, verbose=None, manual=None):
        self.thread_continue = thread_continue or True
        self.verbose = verbose or False
        self.manual = manual or False

mainctrl = MainCtrl()


def main_thread_stop(signum=None, frame=None):
    mainctrl.thread_continue = False


def main_thread(args, mainctrl):
    if hasattr(args, 'manual'):
        mainctrl.manual = True
        core_app.manual_override(args.manual[0])

    try:
        while mainctrl.thread_continue:
            if mainctrl.verbose:
                logger.debug("Continuing...")

            core_app.run()
            time.sleep(config.interval)
    except KeyboardInterrupt as ke:
        if mainctrl.verbose:
            logger.warning("Interrupting...")
    except Exception as e:
        if mainctrl.verbose:
            logger.error("Exception: {0}".format(str(e)))
    finally:
        if not mainctrl.manual:
            rpi_gpio.cleanup()

        if mainctrl.verbose:
            logger.info("Verbose mode end")

        logger.info("Exiting...")


def daemon_start(args=None):
    if hasattr(args, 'verbose'):
        mainctrl.verbose = args.verbose

    if mainctrl.verbose:
        logger.info("Starting {0} with ARGS: {1}".format(config.prog_name, args))
    else:
        logger.info("Starting {0}...".format(config.prog_name))

    if os.path.exists(config.pidpath):
        msg = "{0} is already running".format(config.prog_name)
        print(msg)
        logger.debug(msg + " (according to {0})".format(config.pidpath))
        sys.exit(1)
    else:
        with daemon:
            main_thread(args, mainctrl)


def daemon_stop(args=None):
    if hasattr(args, 'verbose'):
        mainctrl.verbose = args.verbose

    if mainctrl.verbose:
        logger.info("Stopping {0} with ARGS: {1}".format(config.prog_name, args))
    else:
        logger.info("Stopping {0}...".format(config.prog_name))

    if os.path.exists(config.pidpath):
        with open(config.pidpath) as pid:
            try:
                os.kill(int(pid.readline()), signal.SIGINT)
                while os.path.exists(config.pidpath):
                    time.sleep(config.interval)
            except ProcessLookupError as ple:
                os.remove(config.pidpath)
                logger.error("ProcessLookupError: {0}".format(ple))
                return False
            except Exception as e:
                logger.error("Exception: {0}".format(e))
                return False
    else:
        logger.error("Process isn't running (according to the absence of {0}).".format(config.pidpath))

    return True


def daemon_restart(args):
    logger.info("Restarting {0}...".format(config.prog_name))
    logger.debug("Waiting for {0} to stop".format(config.prog_name))
    if daemon_stop():
        daemon_start(args)


def daemon_debug(args):
    logger.info("Running {0} in debug mode".format(config.prog_name))
    main_thread(args, mainctrl)


def daemon_status(args):
    logger.debug("{0} Status {1}".format(config.prog_name, args))

    if os.path.exists(config.pidpath):
        msg = "{0} is running".format(config.prog_name)
        print(msg)
        logger.debug(msg)
    else:
        msg = "{0} is not running".format(config.prog_name)
        print(msg)
        logger.debug(msg)


def daemon_manual(args):
    logger.debug("{0} Manual mode: {1}".format(config.prog_name, args.manual))
    mainctrl.thread_continue = False
    main_thread(args, mainctrl)


daemon = daemon.DaemonContext(
        files_preserve=[
            logg.file_handler.stream,
            logg.console_handler.stream,
        ],
        chroot_directory=config.chroot_dir,
        working_directory=config.working_directory,
        umask=0o002,
        pidfile=daemon.pidfile.PIDLockFile(config.pidpath),
        detach_process=None,
        signal_map={
            signal.SIGTERM: main_thread_stop,
            signal.SIGTSTP: main_thread_stop,
            signal.SIGINT: main_thread_stop,
            #signal.SIGKILL: daemon_stop,
            signal.SIGUSR1: daemon_status,
            signal.SIGUSR2: daemon_status,
        },
        uid=None, #1001
        gid=None, #777
        initgroups=False,
        prevent_core=True,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr
    )

parser = argparse.ArgumentParser(
        prog=config.prog_name,
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

sp_stop.set_defaults(callback=daemon_stop)
sp_status.set_defaults(callback=daemon_status)
sp_start.set_defaults(callback=daemon_start)
sp_restart.set_defaults(callback=daemon_restart)
sp_debug.set_defaults(callback=daemon_debug)
sp_manual.set_defaults(callback=daemon_manual)

args = parser.parse_args()

if hasattr(args, 'callback'):
    args.callback(args)
else:
    parser.print_help()
    #parser.print_usage()
