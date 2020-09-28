import boilr.logger as logg
import boilr.config as config
import boilr.daemon as daemon
import boilr.helpers as helpers
import boilr.rpi_gpio as rpi_gpio

import sys, os
import logging
import requests

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
        daemon.daemon_stop()

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
        #daemon.daemon_stop()
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
        #daemon.daemon_stop()
        pass

    return True
