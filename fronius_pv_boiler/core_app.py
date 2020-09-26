import fronius_pv_boiler.logger as logg
import fronius_pv_boiler.config as config
import fronius_pv_boiler.helpers as helpers
import fronius_pv_boiler.rpi_gpio as rpi_gpio

import sys
import os
import time
import json
import logging
import requests
import daemon
import lockfile
import signal

logger = logging.getLogger(__name__)

#some_important_file = open('some_file', 'rw') # 'r' 'w' 'rw'

def run():
    date_check = helpers.date_checker(config.active_date_range)
    if date_check[0]:

        time_check = helpers.time_checker(config.active_time_range)
        if time_check[0]:

            logger.debug("gathering information")

            response_powerflow = requests.get(config.url + config.api + config.powerflow)

            powerflow_site = response_powerflow.json()['Body']['Data']['Site']
            powerflow_pgrid = powerflow_site['P_Grid'] or 0 # + from grid, - to grid, null no meter enabled
            powerflow_pakku = powerflow_site['P_Akku'] or 0 # + discharge, - charge, null not active
            powerflow_ppv = powerflow_site['P_PV'] or 0 # + production, null inverter not running

            powerflow_inverters = response_powerflow.json()['Body']['Data']['Inverters']['1']
            powerflow_soc = powerflow_inverters['SOC'] # state of charge

            rpi_gpio.gpio_relais(config.rpi_pin_relais)

            if powerflow_soc >= config.charge_threshold and powerflow_pakku < 0 and powerflow_pgrid < 0 and powerflow_ppv > config.ppv_threshold:
                # soc over threshold & storage in charging mode & supply into grid & pv production over threshold
                logger.info("Contactor: closed")
                logger.info("Status: active")
                rpi_gpio.output_relais(config.rpi_pin_relais, 1)
            else:
                logger.info("Contactor: open")
                logger.info("Status: inactive")
                rpi_gpio.output_relais(config.rpi_pin_relais, 0)

        else:
            logger.warning(time_check[1]) # not in time range
            rpi_gpio.cleanup()
    else:
        logger.warning(date_check[1]) # not in date range
        rpi_gpio.cleanup()


def shutdown(signum, frame): # signum and frame are mandatory
    logger.info("Stopping boilr daemon... bye bye")
    sys.exit(0)


daemon = daemon.DaemonContext(
        chroot_directory=None,
        working_directory=config.working_directory,
        files_preserve=[
            logg.file_handler.stream,
            logg.console_handler.stream
        ],
        #pidfile=lockfile.FileLock(config.pid_lockfile),
        stdout=sys.stdout,
        stderr=sys.stderr,
        signal_map={
            signal.SIGTERM: shutdown,
            signal.SIGTSTP: shutdown
        }
    )

logger.info("Starting boilr daemon")

# start daemon
with daemon:
    #print(os.getcwd()) # working directory
    #print(some_important_file.readlines())
    while True:
        run()
        time.sleep(config.interval)
