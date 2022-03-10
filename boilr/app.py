import boilr.config as config
import boilr.daemon as daemon
import boilr.helper as helper
import boilr.rpi_gpio as rpi_gpio

import logging
import requests
import statistics
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Boilr:
    def __init__(self, status=None, status_prev=None, pload: [float]=None, ppv: [float]=None):
        self.status = (status or False, datetime.now())
        self.status_prev = (status_prev or True, datetime.now())
        self.date_check = True
        self.date_check_prev = True
        self.time_check = True
        self.time_check_prev = True
        self.pload = pload or [0]
        self.ppv = ppv or [0]
        self.pload_median = 0
        self.ppv_median = 0


    def update_status(self, state):
        self.status = (state, datetime.now())
        logger.debug("Status updated: {0}".format(state))

boilr = Boilr()


def run():
    ## check date and time range
    (boilr.date_check, date_check_msg) = helper.date_check(config.SystemConfig.active_date_range)
    (boilr.time_check, time_check_msg) = helper.time_check(config.SystemConfig.active_time_range)

    if not boilr.date_check or not boilr.time_check:
        ## check if unchanged
        if boilr.date_check_prev != boilr.date_check:
            logger.info(date_check_msg)
            boilr.date_check_prev = boilr.date_check
            if not boilr.date_check:
                rpi_gpio.cleanup()

        if boilr.time_check_prev != boilr.time_check:
            logger.info(time_check_msg)
            boilr.time_check_prev = boilr.time_check
            if not boilr.time_check:
                rpi_gpio.cleanup()

        return False
    else:
        pass

    try:
        inverter_url = config.EndpointConfig.scheme + config.EndpointConfig.ip
        logger.debug("Gathering information from endpoint at: {0}".format(inverter_url))

        response_powerflow = requests.get(
                inverter_url + config.EndpointConfig.api + config.EndpointConfig.powerflow,
                timeout=config.EndpointConfig.request_timeout
            )
    except requests.exceptions.ConnectionError as e: # network problem
        logger.warning("Connection error: {0}".format(str(e)))
    except requests.exceptions.Timeout as e:
        logger.warning("Request timeout: {0}".format(str(e)))
    except requests.exceptions.TooManyRedirects as e:
        logger.warning("Too many redirects: {0}".format(str(e)))
    except requests.exceptions.RequestException as e:
        logger.warning("There was an error with the request: {0}".format(str(e)))
    except Exception as e:
        logger.error("Unrecoverable error in request: {0}".format(str(e)))
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

        if len(boilr.pload) >= config.SystemConfig.moving_median_list_size:
            del boilr.ppv[0]
            del boilr.pload[0]

        boilr.pload.append(powerflow_pload)
        boilr.ppv.append(powerflow_ppv)
        boilr.pload_median = statistics.median(boilr.pload)
        boilr.ppv_median = statistics.median(boilr.ppv)

        logger.debug("Median power ppv: {0} W".format(boilr.ppv_median))
        logger.debug("Median power load: {0} W".format(boilr.pload_median))

        powerflow_inverters = response_powerflow.json()['Body']['Data']['Inverters']['1']
        powerflow_soc = powerflow_inverters['SOC'] # state of charge

        logger.debug("SOC: {0} %".format(powerflow_soc))

        ## set gpio mode
        if not rpi_gpio.gpio_mode(config.RpiConfig.rpi_channel_relay_out, "out"):
            logger.warning("Error while setting gpio mode for: output")
            logger.debug("skipping condition evaluation")
            return False
        else:
            logger.debug("Checking conditions")
            if (powerflow_soc >= config.SystemConfig.charge_threshold and # soc over threshold
                boilr.ppv_median > (
                    (config.SystemConfig.heater_power if not boilr.status_prev[0] else 0)
                    + abs(boilr.pload_median)
                    - config.SystemConfig.ppv_tolerance
                ) # median pv production is over median load + expected load with tolerance
            ):
                boilr.update_status(True)
            else:
                boilr.update_status(False)

            ## check start timeout (instant off, delayed starting)
            if boilr.status_prev[0] or not boilr.status_prev[0] and boilr.status_prev[1] < datetime.now() - timedelta(seconds=config.SystemConfig.start_timeout):
                ## check if status unchanged
                if boilr.status_prev[0] != boilr.status[0]:
                    logger.debug("Conditions {0} met: contactor {1}".format("not" if not boilr.status[0] else "", "closed" if boilr.status[0] else "open"))
                    logger.info("Status: {0}".format("active" if boilr.status[0] else "inactive"))
                    boilr.status_prev = boilr.status

                    if not rpi_gpio.output_relay(config.RpiConfig.rpi_channel_relay_out, boilr.status[0]):
                        logger.warning("Error while setting gpio channel")
                        return False
                else:
                    logger.debug("Contactor unchanged - previous state: {0}".format(boilr.status_prev[0]))

        ## read relay channel
        if not rpi_gpio.gpio_mode(config.RpiConfig.rpi_channel_relay_in, "in"):
            logger.warning("Error while setting gpio mode for: input")
            return False
        elif not rpi_gpio.input_relay(config.RpiConfig.rpi_channel_relay_in):
            logger.warning("Error while reading gpio channel")
            return False
        else:
            pass

    finally:
        return True


def manual_override(args):
    if not rpi_gpio.gpio_mode(config.RpiConfig.rpi_channel_relay_out, "out") or not rpi_gpio.gpio_mode(config.RpiConfig.rpi_channel_relay_in, "in"):
        logger.warning("Error while setting gpio mode")
        return False

    if args in {0, 1}:
        logger.debug("Manual override: contactor {0}".format("closed" if args == 1 else "open"))
        logger.info("Status: {0} (manual)".format("active" if args == 1 else "inactive"))
        gpio_output = rpi_gpio.output_relay(config.RpiConfig.rpi_channel_relay_out, True if args == 1 else False)
    else:
        logger.warning("Manual override failed. Wrong argument: {0}".format(args))

    return True
