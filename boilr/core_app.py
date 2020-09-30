import boilr.logger as logg
import boilr.config as config
import boilr.daemon as daemon
import boilr.helpers as helpers
import boilr.rpi_gpio as rpi_gpio

import sys, os
import time
import logging
import requests

logger = logging.getLogger(__name__)

def run():
    if not helpers.date_checker(config.active_date_range)[0]:
        rpi_gpio.cleanup()
        return False

    if not helpers.time_checker(config.active_time_range)[0]:
        rpi_gpio.cleanup()
        return False

    logger.debug("Gathering information")
    inverter_url = config.scheme + config.ip

    try:
        response_powerflow = requests.get(inverter_url + config.api + config.powerflow, timeout=config.request_timeout)
    except requests.exceptions.ConnectionError as e: # network problem
        logger.warning("Connection error")
    except requests.exceptions.Timeout as e:
        logger.warning("Request timeout")
    except requests.exceptions.TooManyRedirects as e:
        logger.warning("Too many redirects")
    except requests.exceptions.RequestException as e:
        logger.warning("There was an error with the request")
    except Exception as e:
        logger.error("Unrecoverable error in request")
        daemon.daemon_stop()
        #raise SystemExit(e)

    powerflow_site = response_powerflow.json()['Body']['Data']['Site']
    powerflow_pgrid = powerflow_site['P_Grid'] or 0 # + from grid, - to grid, null no meter enabled
    powerflow_pakku = powerflow_site['P_Akku'] or 0 # + discharge, - charge, null not active
    powerflow_ppv = powerflow_site['P_PV'] or 0 # + production, null inverter not running

    logger.debug("Powerflow grid: {0} W".format(powerflow_pgrid))
    logger.debug("Powerflow akku: {0} W".format(powerflow_pakku))
    logger.debug("Powerflow ppv: {0} W".format(powerflow_ppv))

    powerflow_inverters = response_powerflow.json()['Body']['Data']['Inverters']['1']
    powerflow_soc = powerflow_inverters['SOC'] # state of charge

    logger.debug("SOC: {0} %".format(powerflow_soc))

    if not rpi_gpio.gpio_mode(config.rpi_channel_relais_out, "out") or not rpi_gpio.gpio_mode(config.rpi_channel_relais_in, "in"):
        logger.warning("Error while setting gpio mode")
        #daemon.daemon_stop()

    logger.debug("Checking confitions")
    if powerflow_soc >= config.charge_threshold and powerflow_pakku < 0 and powerflow_pgrid < 0 and powerflow_ppv > config.ppv_threshold:
        # soc over threshold & storage in charging mode & supply into grid & pv production over threshold
        logger.debug("Conditions not met: contactor closed")
        logger.info("Status: active")
        gpio_output = rpi_gpio.output_relais(config.rpi_channel_relais_out, 1)
    else:
        logger.debug("Conditions met: contactor open")
        logger.info("Status: inactive")
        gpio_output = rpi_gpio.output_relais(config.rpi_channel_relais_out, 0)

    time.sleep(1)

    if not gpio_output:
        logger.warning("Error while setting gpio channel")
        #daemon.daemon_stop()
    elif not rpi_gpio.input_relais(config.rpi_channel_relais_in):
        logger.warning("Error while reading gpio channel")
        #daemon.daemon_stop()

    return True
