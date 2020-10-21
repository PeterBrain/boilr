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

class Boilr:
    def __init__(self, status=None, status_prev=None):
        self.status = status or False
        self.status_prev = status_prev or True

boilr = Boilr()


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
    else:
        powerflow_site = response_powerflow.json()['Body']['Data']['Site']
        powerflow_pgrid = powerflow_site['P_Grid'] or 0 # + from grid, - to grid, null no meter enabled
        powerflow_pakku = powerflow_site['P_Akku'] or 0 # + discharge, - charge, null not active
        powerflow_ppv = powerflow_site['P_PV'] or 0 # + production, null inverter not running
        powerflow_pload = powerflow_site['P_Load'] or 0 # - current load

        logger.debug("Powerflow grid: {0} W".format(powerflow_pgrid))
        logger.debug("Powerflow akku: {0} W".format(powerflow_pakku))
        logger.debug("Powerflow ppv: {0} W".format(powerflow_ppv))
        logger.debug("Powerflow load: {0} W".format(powerflow_pload))

        powerflow_inverters = response_powerflow.json()['Body']['Data']['Inverters']['1']
        powerflow_soc = powerflow_inverters['SOC'] # state of charge

        logger.debug("SOC: {0} %".format(powerflow_soc))

        if not rpi_gpio.gpio_mode(config.rpi_channel_relay_out, "out"):
            logger.warning("Error while setting gpio mode for: output")
            logger.debug("skipping condition evaluation")
            return False
        else:
            logger.debug("Checking conditions")
            if (powerflow_soc >= config.charge_threshold and # soc over threshold
                powerflow_pakku < config.pakku_threshold and # storage in charging mode (with threshold)
                powerflow_pgrid < config.pgrid_threshold and # supply into grid (with threshold)
                powerflow_ppv > (config.heater_power + powerflow_pload - config.ppv_threshold) # pv production over current load + expected load with threshold
            ):
                boilr.status = True
            else:
                boilr.status = False

            if boilr.status_prev != boilr.status:
                logger.debug("Conditions {0} met: contactor {1}".format("not" if not boilr.status else "", "closed" if boilr.status else "open"))
                logger.info("Status: {0}".format("active" if boilr.status else "inactive"))
            else:
                logger.debug("Contactor unchanged - previous state: {0}".format(boilr.status_prev))

            boilr.status_prev = boilr.status

            if not rpi_gpio.output_relay(config.rpi_channel_relay_out, boilr.status):
                logger.warning("Error while setting gpio channel")
                return False

        if not rpi_gpio.gpio_mode(config.rpi_channel_relay_in, "in"):
            logger.warning("Error while setting gpio mode for: input")
            return False
        else:
            if not rpi_gpio.input_relay(config.rpi_channel_relay_in):
                logger.warning("Error while reading gpio channel")
                return False

    finally:
        return True


def manual_override(args):
    if not rpi_gpio.gpio_mode(config.rpi_channel_relay_out, "out") or not rpi_gpio.gpio_mode(config.rpi_channel_relay_in, "in"):
        logger.warning("Error while setting gpio mode")
        return False

    if args in {0, 1}:
        logger.debug("Manual override: contactor {0}".format("closed" if args == 1 else "open"))
        logger.info("Status: {0} (manual)".format("active" if args == 1 else "inactive"))
        gpio_output = rpi_gpio.output_relay(config.rpi_channel_relay_out, True if args == 1 else False)
    else:
        logger.warning("Manual override failed. Wrong argument: {0}".format(args))

    return True
