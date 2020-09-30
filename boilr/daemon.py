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

class MainCtrl:
    thread_continue = True

mainctrl = MainCtrl()

def main_thread_stop(signum=None, frame=None):
    mainctrl.thread_continue = False


def main_thread(args, mainctrl):
    verbose = False

    if hasattr(args, 'verbose'):
        verbose = args.verbose
        logger.info("ARGS: {0}".format(args))

    try:
        while mainctrl.thread_continue:
            if verbose:
                logger.debug("Continuing...")

            core_app.run()
            time.sleep(config.interval)
    except KeyboardInterrupt as ke:
        if verbose:
            logger.warning("Interrupting...")
    except Exception as e:
        if verbose:
            logger.error("Exception: {0}".format(str(e)))
    finally:
        rpi_gpio.cleanup()
        logger.info("Exiting...")
        #sys.exit(0)


def daemon_start(args=None):
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
    logger.info("Stopping {0} with args {1}".format(config.prog_name, args))

    if os.path.exists(config.pidpath):
        with open(config.pidpath) as pid:
            try:
                os.kill(int(pid.readline()), signal.SIGINT)
            except ProcessLookupError as ple:
                os.remove(config.pidpath)
                logger.error("ProcessLookupError: {0}".format(ple))
            except Exception as e:
                logger.error("Exception: {0}".format(e))
    else:
        logger.error("Process isn't running (according to the absence of {0}).".format(config.pidpath))


def daemon_restart(args):
    logger.info("Restarting {0}...".format(config.prog_name))
    daemon_stop()
    time.sleep(1)
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


daemon = daemon.DaemonContext(
        files_preserve=[
            logg.file_handler.stream,
            logg.console_handler.stream
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

parser = argparse.ArgumentParser(prog = config.prog_name)
sp = parser.add_subparsers()
sp_start = sp.add_parser('start', help='Starts %(prog)s daemon')
sp_stop = sp.add_parser('stop', help='Stops %(prog)s daemon')
sp_status = sp.add_parser('status', help='Show the status of %(prog)s daemon')
sp_restart = sp.add_parser('restart', help='Restarts %(prog)s daemon')
sp_debug = sp.add_parser('debug', help='Starts %(prog)s daemon in debug mode')
sp_start.add_argument('-v', '--verbose', action='store_true', help='log extra informations')
sp_debug.add_argument('-v', '--verbose', action='store_true', help='log extra informations')

sp_stop.set_defaults(callback=daemon_stop)
sp_status.set_defaults(callback=daemon_status)
sp_start.set_defaults(callback=daemon_start)
sp_restart.set_defaults(callback=daemon_restart)
sp_debug.set_defaults(callback=daemon_debug)
args = parser.parse_args()

if hasattr(args, 'callback'):
    args.callback(args)
else:
    parser.print_help()
