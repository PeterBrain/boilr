"""Daemon module"""
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

logger = logging.getLogger(__name__)


def is_verbose(args):
    """
    Global verbosity store

    Parameters
    ----------
    args : obj
        Command line arguments
    """
    if hasattr(args, 'verbose') and getattr(args, 'verbose'):
        core.mainctrl.verbose = args.verbose
        logg.console_handler.setLevel(logging.DEBUG)


def daemon_start(args=None):
    """
    Starting daemon with args - start main thread

    Parameters
    ----------
    args : obj, optional
        Command line arguments (default is None)
    """
    is_verbose(args)
    config.initialize(args)

    logger.info("Starting %s service", config.SystemConfig.prog_name)
    logger.debug(
        "Attempt to start daemon with pid file: %s",
        config.SystemConfig.pidpath
    )

    if core.mainctrl.verbose:
        logger.debug(
            "Starting %s with ARGS: %s",
            config.SystemConfig.prog_name,
            args
        )
    else:
        logger.info("Starting %s...", config.SystemConfig.prog_name)

    if os.path.exists(config.SystemConfig.pidpath):
        msg = f"{config.SystemConfig.prog_name} is already running"
        print(msg)
        logger.debug("%s (according to %s)", msg, config.SystemConfig.pidpath)
        sys.exit(1)
    else:
        daemon_context = init_daemon()
        with daemon_context:
            core.main_thread(args, core.mainctrl)


def daemon_stop(args=None):
    """
    Stopping daemon with args - stop main thread

    Parameters
    ----------
    args : obj, optional
        Command line arguments (default is None)

    Raises
    ------
    ToDo
    Exception
        General exception
    """
    is_verbose(args)

    if core.mainctrl.verbose:
        logger.info(
            "Stopping %s with ARGS: %s",
            config.SystemConfig.prog_name,
            args
        )
    else:
        logger.info("Stopping %s...", config.SystemConfig.prog_name)

    if os.path.exists(config.SystemConfig.pidpath):
        with open(config.SystemConfig.pidpath, "r", encoding="utf-8") as pid:
            try:
                os.kill(int(pid.readline()), signal.SIGINT)  # kill process

                wait = "Stopping.."
                while os.path.exists(config.SystemConfig.pidpath):
                    if core.mainctrl.verbose:
                        print(wait, sep='', end='\r', flush=True)
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
                logger.warning(
                    "Attempting process %s cleanup",
                    config.SystemConfig.prog_name
                )
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
    """
    Restarting daemon with args

    Parameters
    ----------
    args : obj
        Command line arguments
    """
    is_verbose(args)

    logger.info("Restarting %s...", config.SystemConfig.prog_name)
    logger.debug("Waiting for %s to stop", config.SystemConfig.prog_name)

    if daemon_stop():
        logger.debug(
            "%s stopped. Attempting to start again",
            config.SystemConfig.prog_name
        )
        daemon_start(args)


def daemon_run(args):
    """
    Running daemon interactively with args

    Parameters
    ----------
    args : obj
        Command line arguments
    """
    logg.console_handler.setLevel(logging.WARN)
    is_verbose(args)
    config.initialize(args)

    logger.info(
        "Starting %s in interactive mode",
        config.SystemConfig.prog_name
    )
    core.main_thread(args, core.mainctrl)


def daemon_status(args):
    """
    Printing status of daemon with args

    Due to memory separation in daemon,
    status variables from Boilr class are disabled.

    Parameters
    ----------
    args : obj
        Command line arguments
    """
    is_verbose(args)

    if core.mainctrl.verbose:
        logger.info(
            "%s status with ARGS: %s",
            config.SystemConfig.prog_name,
            args
        )
    else:
        logger.debug("%s Status: %s", config.SystemConfig.prog_name, args)

    if os.path.exists(config.SystemConfig.pidpath):
        msg = f"{config.SystemConfig.prog_name} service is running"
        logger.debug(msg)

        with open(config.SystemConfig.pidpath, "r", encoding="utf-8") as pid:
            process_id = int(pid.readline())
            msg += f"\nProcess id: {process_id}"

        msg += f"\nPID file: {config.SystemConfig.pidpath}"
        msg += f"\nLOG file: {config.SystemConfig.logpath}"
        msg += f"\nConf file: {config.SystemConfig.config_file}"

        # Status variables disabled due to memory separation in daemon
        # suggestion: multiprocessing.Manager for shared state (shared_dict)

        print(msg)
    else:
        msg = f"{config.SystemConfig.prog_name} service is not running"
        print(msg)
        logger.debug(msg)


def daemon_manual(args):
    """
    Manually setting contactor output

    - Daemon -> will be stopped and output overridden
    - Interactively -> continues and output will be overridden

    Parameters
    ----------
    args : obj
        Command line arguments
    """
    is_verbose(args)
    config.initialize(args)

    logger.debug(
        "%s Manual mode: %s",
        config.SystemConfig.prog_name,
        args.manual
    )
    core.mainctrl.thread_continue = False
    core.main_thread(args, core.mainctrl)


def init_daemon():
    """
    Initialize daemon context

    Returns
    -------
    DaemonContext
    """
    daemon_context = daemon.DaemonContext(
        files_preserve=[  # preserve logging handler
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
            # signal.SIGKILL: daemon_stop,
            signal.SIGUSR1: daemon_status,
            signal.SIGUSR2: daemon_status,
        },
        uid=None,
        gid=None,
        initgroups=False,
        prevent_core=True,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    return daemon_context
