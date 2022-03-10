import boilr.logger as logg
import boilr.config as config
import boilr.core as core

import sys, os
import time
import logging
import signal
import daemon
from daemon import pidfile

logger = logging.getLogger(__name__)

def daemon_start(args=None):
    if hasattr(args, 'verbose'):
        core.mainctrl.verbose = args.verbose

    if core.mainctrl.verbose:
        logger.info("Starting {0} with ARGS: {1}".format(config.SystemConfig.prog_name, args))
    else:
        logger.info("Starting {0}...".format(config.SystemConfig.prog_name))

    if os.path.exists(config.SystemConfig.pidpath):
        msg = "{0} is already running".format(config.SystemConfig.prog_name)
        print(msg)
        logger.debug(msg + " (according to {0})".format(config.SystemConfig.pidpath))
        sys.exit(1)
    else:
        with daemon:
            core.main_thread(args, core.mainctrl)


def daemon_stop(args=None):
    if hasattr(args, 'verbose'):
       core.mainctrl.verbose = args.verbose

    if core.mainctrl.verbose:
        logger.info("Stopping {0} with ARGS: {1}".format(config.SystemConfig.prog_name, args))
    else:
        logger.info("Stopping {0}...".format(config.SystemConfig.prog_name))

    if os.path.exists(config.SystemConfig.pidpath):
        with open(config.SystemConfig.pidpath) as pid:
            try:
                os.kill(int(pid.readline()), signal.SIGINT)
                while os.path.exists(config.SystemConfig.pidpath):
                    time.sleep(config.SystemConfig.interval)
            except ProcessLookupError as ple:
                os.remove(config.SystemConfig.pidpath)
                logger.error("ProcessLookupError: {0}".format(ple))
                return False
            except OSError as ose:
                logger.error("Process {0} could not be terminated: {1}".format(config.SystemConfig.prog_name, ose))
                logger.warning("Attempting process {0} cleanup".format(config.SystemConfig.prog_name))
                os.remove(config.SystemConfig.pidpath)
                sys.exit(1)
            except Exception as e:
                logger.error("Exception: {0}".format(e))
                return False
            else:
                logger.info("Process is now stopped")

    else:
        logger.error("Process isn't running (according to the absence of {0}).".format(config.SystemConfig.pidpath))

    return True


def daemon_restart(args):
    logger.info("Restarting {0}...".format(config.SystemConfig.prog_name))
    logger.debug("Waiting for {0} to stop".format(config.SystemConfig.prog_name))
    if daemon_stop():
        daemon_start(args)


def daemon_debug(args):
    logger.info("Running {0} in debug mode".format(config.SystemConfig.prog_name))
    core.main_thread(args, core.mainctrl)


def daemon_status(args):
    logger.debug("{0} Status {1}".format(config.SystemConfig.prog_name, args))

    if os.path.exists(config.SystemConfig.pidpath):
        msg = "{0} is running".format(config.SystemConfig.prog_name)
        print(msg)
        logger.debug(msg)
    else:
        msg = "{0} is not running".format(config.SystemConfig.prog_name)
        print(msg)
        logger.debug(msg)


def daemon_manual(args):
    logger.debug("{0} Manual mode: {1}".format(config.SystemConfig.prog_name, args.manual))
    core.mainctrl.thread_continue = False
    core.main_thread(args, core.mainctrl)


daemon = daemon.DaemonContext(
        files_preserve=[ # preserve logging handler
            logg.file_handler.stream,
            logg.console_handler.stream,
        ],
        chroot_directory=config.SystemConfig.chroot_dir,
        working_directory=config.SystemConfig.working_directory,
        umask=0o002,
        pidfile=daemon.pidfile.PIDLockFile(config.SystemConfig.pidpath),
        detach_process=None,
        signal_map={
            signal.SIGTERM: core.mainctrl.main_thread_stop,
            signal.SIGTSTP: core.mainctrl.main_thread_stop,
            signal.SIGINT: core.mainctrl.main_thread_stop,
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
