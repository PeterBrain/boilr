"""Daemon module"""
import os
import sys
import time
import logging
import signal
import daemon
from daemon import pidfile

import boilr.core as core

logger = logging.getLogger(__name__)


def daemon_start(ctx=None):
    """Starting daemon with args - start main thread"""
    logger.info("Starting %s service", ctx.config.system.prog_name)
    logger.debug("Starting %s with ARGS: %s", ctx.config.system.prog_name, ctx.args)

    if os.path.exists(ctx.config.system.pidpath):
        msg = f"{ctx.config.system.prog_name} is already running"
        logger.debug("%s (according to %s)", msg, ctx.config.system.pidpath)
        print(msg)
        sys.exit(1)
    else:
        logger.debug("Attempt to start daemon with pid file: %s", ctx.config.system.pidpath)
        daemon_context = init_daemon(ctx)
        with daemon_context:
            core.main_thread(ctx)


def daemon_stop(ctx=None):
    """Stopping daemon with args - stop main thread"""
    logger.info("Stopping %s with ARGS: %s", ctx.config.system.prog_name, ctx.args)

    if os.path.exists(ctx.config.system.pidpath):
        with open(ctx.config.system.pidpath, "r", encoding="utf-8") as pid_file:
            try:
                pid = int(pid_file.readline())
                os.kill(pid, signal.SIGINT)  # kill process

                wait = "Stopping.."
                while os.path.exists(ctx.config.system.pidpath):
                    if ctx.main_ctrl.verbose:
                        print(wait, sep="", end="\r", flush=True)
                        time.sleep(1)
                        wait += "."

                if ctx.main_ctrl.verbose:
                    print(wait + " OK")

            except ProcessLookupError as ple:
                os.remove(ctx.config.system.pidpath)
                logger.error("ProcessLookupError: %s", ple)
                return False
            except OSError as ose:
                logger.error("Process could not be terminated: %s", ose)
                logger.warning("Attempting process %s cleanup", ctx.config.system.prog_name)
                os.remove(ctx.config.system.pidpath)
                sys.exit(1)  # exit with error (return False unreachable)
            except Exception as e_general:
                logger.error("Exception: %s", e_general)
                return False
            else:
                logger.info("Process is now stopped")
                return True

    else:
        logger.error("Process is not running (absent PID file at: %s).", ctx.config.system.pidpath)
        return False


def daemon_restart(ctx):
    """Restarting daemon with args"""
    logger.info("Restarting %s...", ctx.config.system.prog_name)
    logger.debug("Waiting for %s to stop", ctx.config.system.prog_name)

    if daemon_stop(ctx):
        logger.debug("%s stopped. Attempting to start again", ctx.config.system.prog_name)
        daemon_start(ctx)


def daemon_run(ctx):
    """Running daemon interactively with args"""
    logger.debug("%s run with ARGS: %s", ctx.config.system.prog_name, ctx.args)
    logger.info("Starting %s in interactive mode", ctx.config.system.prog_name)
    core.main_thread(ctx)


def daemon_status(ctx):
    """
    Printing status of daemon with args

    Due to memory separation in daemon,
    status variables from Boilr class are disabled.
    """
    logger.debug("%s status with ARGS: %s", ctx.config.system.prog_name, ctx.args)

    if os.path.exists(ctx.config.system.pidpath):
        msg = f"{ctx.config.system.prog_name} service is running"

        if ctx.main_ctrl.verbose:
            logger.debug(msg)
        else:
            with open(ctx.config.system.pidpath, "r", encoding="utf-8") as pid:
                process_id = int(pid.readline())
                msg += f"\nProcess id: {process_id}"

            msg += f"\nPID file: {ctx.config.system.pidpath}"
            msg += f"\nLOG file: {ctx.config.system.logpath}"
            msg += f"\nConf file: {ctx.config.system.config_file}"

            # Status variables disabled due to memory separation in daemon
            # suggestion: multiprocessing.Manager for shared state (shared_dict)

            print(msg)
    else:
        msg = f"{ctx.config.system.prog_name} service is not running"

        if ctx.main_ctrl.verbose:
            logger.debug(msg)
        else:
            print(msg)


def daemon_manual(ctx):
    """
    Manually override contactor

    - Daemon -> will be stopped and output overridden
    - Interactively -> continues and output will be overridden
    """
    logger.debug("%s Manual mode: %s", ctx.config.system.prog_name, ctx.args.manual)
    core.main_thread(ctx)


def init_daemon(ctx):
    """Initialize daemon context"""
    daemon_context = daemon.DaemonContext(
        files_preserve=[  # preserve logging handler
            ctx.file_handler.stream,  #getattr(ctx.file_handler, "stream", None),
            ctx.console_handler.stream,  #getattr(ctx.console_handler, "stream", None),
        ],
        chroot_directory=ctx.config.system.chroot_dir,
        working_directory=ctx.config.system.working_directory,
        umask=0o002,
        pidfile=pidfile.PIDLockFile(ctx.config.system.pidpath),
        detach_process=True,
        signal_map={
            signal.SIGTERM: ctx.main_ctrl.main_thread_stop,
            signal.SIGTSTP: ctx.main_ctrl.main_thread_stop,
            signal.SIGINT: ctx.main_ctrl.main_thread_stop,
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
