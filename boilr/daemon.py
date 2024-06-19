"""daemon"""
import sys
import os
import time
import logging
import signal
import daemon
from daemon import pidfile

import boilr.logger as logg
import boilr.config as config
import boilr.core as core
import boilr.app as app

logger = logging.getLogger(__name__)

def is_verbose(args):
    """Function global verbosity store"""
    if hasattr(args, 'verbose') and getattr(args, 'verbose'):
        core.mainctrl.verbose = args.verbose
        logg.console_handler.setLevel(logging.DEBUG)


def daemon_start(args=None):
    """Function starting daemon with args - start main thread"""
    is_verbose(args)

    if core.mainctrl.verbose:
        logger.info("Starting %s with ARGS: %s", config.SystemConfig.prog_name, args)
    else:
        logger.info("Starting %s...", config.SystemConfig.prog_name)

    if os.path.exists(config.SystemConfig.pidpath):
        msg = f"{config.SystemConfig.prog_name} is already running"
        print(msg)
        logger.debug("%s (according to %s)", msg, config.SystemConfig.pidpath)
        sys.exit(1)
    else:
        with daemon:
            core.main_thread(args, core.mainctrl)


def daemon_stop(args=None):
    """Function stopping daemon with args - stop main thread"""
    is_verbose(args)

    if core.mainctrl.verbose:
        logger.info("Stopping %s with ARGS: %s", config.SystemConfig.prog_name, args)
    else:
        logger.info("Stopping %s...", config.SystemConfig.prog_name)

    if os.path.exists(config.SystemConfig.pidpath):
        with open(config.SystemConfig.pidpath, "r", encoding="utf-8") as pid:
            try:
                os.kill(int(pid.readline()), signal.SIGINT) # kill process via DaemonContext

                wait="Stopping.."
                while os.path.exists(config.SystemConfig.pidpath):
                    if core.mainctrl.verbose:
                        print(wait, sep='', end ='\r', flush=True)
                        time.sleep(1)
                        wait += "."

                if core.mainctrl.verbose:
                    print(wait + " OK")

            except ProcessLookupError as ple:
                os.remove(config.SystemConfig.pidpath)
                logger.error("ProcessLookupError: %s", ple)
                return False
            except OSError as ose:
                logger.error(
                    "Process %s could not be terminated: %s",
                    config.SystemConfig.prog_name,
                    ose
                )
                logger.warning("Attempting process %s cleanup", config.SystemConfig.prog_name)
                os.remove(config.SystemConfig.pidpath)
                sys.exit(1)
            except Exception as e_general:
                logger.error("Exception: %s", e_general)
                return False
            else:
                logger.info("Process is now stopped")

    else:
        logger.error(
            "Process isn't running (according to the absence of %s).",
            config.SystemConfig.pidpath
        )

    return True


def daemon_restart(args):
    """Function restarting daemon with args"""
    is_verbose(args)

    logger.info("Restarting %s...", config.SystemConfig.prog_name)
    logger.debug("Waiting for %s to stop", config.SystemConfig.prog_name)

    if daemon_stop():
        logger.debug("%s stopped. Attempting to start again", config.SystemConfig.prog_name)
        daemon_start(args)


def daemon_run(args):
    """Function running daemon with args"""
    logg.console_handler.setLevel(logging.WARN)
    is_verbose(args)

    logger.info("Running %s in debug mode", config.SystemConfig.prog_name)
    core.main_thread(args, core.mainctrl)


def daemon_status(args):
    """Function printing status of daemon with args"""
    is_verbose(args)

    if core.mainctrl.verbose:
        logger.info("%s status with ARGS: %s", config.SystemConfig.prog_name, args)
    else:
        logger.debug("%s Status: %s", config.SystemConfig.prog_name, args)

    if os.path.exists(config.SystemConfig.pidpath):
        boilr = app.boilr
        (status, status_timestamp) = boilr.status
        (status_prev, status_timestamp_prev) = boilr.status

        msg = f"{config.SystemConfig.prog_name} is running"
        logger.debug(msg)

        msg += f"\nContactor status: {status}"
        msg += f"\nContactor last changed: {status_timestamp}"
        msg += f"\nContactor {'closed' if status else 'open'} for \
            {round((status_timestamp - status_timestamp_prev).total_seconds())} \
            seconds, Previously {status_prev}"
        msg += f"\nPower load: {boilr.pload} W, Median: {boilr.pload_median} W"
        msg += f"\nPower pv: {boilr.ppv} W, Median: {boilr.ppv_median} W"
        print(msg)
    else:
        msg = f"{config.SystemConfig.prog_name} is not running"
        print(msg)
        logger.debug(msg)


def daemon_manual(args):
    """Function manually setting contactor output"""
    is_verbose(args)

    logger.debug("%s Manual mode: %s", config.SystemConfig.prog_name, args.manual)
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
    pidfile=pidfile.PIDLockFile(config.SystemConfig.pidpath),
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
