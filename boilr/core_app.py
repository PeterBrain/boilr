import boilr.logger as logg
import boilr.config as config
import boilr.helpers as helpers
import boilr.rpi_gpio as rpi_gpio

import sys
import os
import time
import json
import logging
import signal
import requests
import daemon # https://github.com/python/peps/blob/master/pep-3143.txt
from daemon import pidfile
#import fasteners

logger = logging.getLogger(__name__)

def run():
    date_check = helpers.date_checker(config.active_date_range)
    if not date_check[0]:
        rpi_gpio.cleanup()
        return False

    time_check = helpers.time_checker(config.active_time_range)
    if not time_check[0]:
        rpi_gpio.cleanup()
        return False

    logger.debug("gathering information")
    inverter_url = config.scheme + config.ip

    try:
        response_powerflow = requests.get(inverter_url + config.api + config.powerflow, timeout=config.request_timeout)
    #except requests.exceptions.ConnectionError as e: # network problem
    #    return False
    #except requests.exceptions.Timeout as e:
    #    return False
    #except requests.exceptions.TooManyRedirects as e:
    #    return False
    #except requests.exceptions.RequestException as e:
    except:
        #raise SystemExit(e)
        shutdown(9, sys.exc_info())

    powerflow_site = response_powerflow.json()['Body']['Data']['Site']
    powerflow_pgrid = powerflow_site['P_Grid'] or 0 # + from grid, - to grid, null no meter enabled
    powerflow_pakku = powerflow_site['P_Akku'] or 0 # + discharge, - charge, null not active
    powerflow_ppv = powerflow_site['P_PV'] or 0 # + production, null inverter not running

    logger.debug("Powerflow grid: " + str(powerflow_pgrid) + " W")
    logger.debug("Powerflow akku: " + str(powerflow_pakku) + " W")
    logger.debug("Powerflow ppv: " + str(powerflow_ppv) + " W")

    powerflow_inverters = response_powerflow.json()['Body']['Data']['Inverters']['1']
    powerflow_soc = powerflow_inverters['SOC'] # state of charge

    logger.debug("SOC: " + str(powerflow_soc) + " %")

    if not rpi_gpio.gpio_relais(config.rpi_pin_relais):
        #shutdown(9,"Error with GPIO")
        pass

    logger.debug("checking confitions")
    if powerflow_soc >= config.charge_threshold and powerflow_pakku < 0 and powerflow_pgrid < 0 and powerflow_ppv > config.ppv_threshold:
        # soc over threshold & storage in charging mode & supply into grid & pv production over threshold
        logger.debug("conditions not met: contactor closed")
        logger.info("Status: active")
        gpio_output = rpi_gpio.output_relais(config.rpi_pin_relais, 1)
    else:
        logger.debug("conditions met: contactor open")
        logger.info("Status: inactive")
        gpio_output = rpi_gpio.output_relais(config.rpi_pin_relais, 0)

    if not gpio_output:
        #shutdown(9,"Error with GPIO")
        pass

    return True


def shutdown(signum, frame): # signum and frame are mandatory
    logger.debug("signal " + str(signum) + " received. Shutting down.")
    logger.info("Stopping boilr daemon... bye bye")
    #daemon.close()
    daemon.terminate(signum, frame)
    sys.exit(0)


daemon = daemon.DaemonContext(
        files_preserve=[
            logg.file_handler.stream,
            logg.console_handler.stream
        ],
        chroot_directory=config.chroot_dir,
        working_directory=config.working_directory,
        umask=0o002,
        pidfile=daemon.pidfile.PIDLockFile(config.pid_lockfile),#lockfile.FileLock(config.pid_lockfile),
        detach_process=None,
        signal_map={
            #'SIGTTIN': None,
            #'SIGTTOU': None,
            signal.SIGTERM: shutdown,
            signal.SIGTSTP: shutdown
        },
        uid=None, #1001
        gid=None, #777
        initgroups=False,
        prevent_core=True,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr
    )

logger.info("Starting boilr daemon")

# start daemon
if os.path.exists(config.pid_lockfile):
    logger.debug("Another instance of this daemon already running (according to {0})".format(config.pid_lockfile))
    logger.error("Daemon already running")
    sys.exit(1)
else:
    #os.makedirs(os.path.dirname(config.working_directory), exist_ok=True) # maybe needs elevated privileges
    with daemon:
        while True:
            run()
            time.sleep(config.interval)
