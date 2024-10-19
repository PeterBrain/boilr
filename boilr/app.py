"""App module"""
import logging
import statistics
from datetime import datetime, timedelta
from typing import List
from collections import deque
from urllib3.util import Retry
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as RequestsConnectionError, \
    Timeout, TooManyRedirects, RequestException

import boilr.config as config
import boilr.daemon as daemon
import boilr.helper as helper
import boilr.rpi_gpio as rpi_gpio
from boilr.mqtt import publish_mqtt

logger = logging.getLogger(__name__)

class Boilr:
    """
    Boilr class

    holds all status variables
    """
    def __init__(
        self, status=None,
        status_prev=None,
        pload: List[float]=None,
        ppv: List[float]=None
    ):
        self.status = (status or False, datetime.now())
        self.status_prev = (status_prev or False, datetime.now())
        self.date_check = True
        self.date_check_prev = True
        self.time_check = True
        self.time_check_prev = True
        self.pload = pload or deque(maxlen=config.SystemConfig.moving_median_list_size)
        self.ppv = ppv or deque(maxlen=config.SystemConfig.moving_median_list_size)
        self.pload_median = 0
        self.ppv_median = 0

    def update_status(self, state):
        """
        Update contactor status

        Parameters:
        -----------
        state : bool
            State of the contactor

        Returns:
        --------
        bool = True
        """
        self.status = (state, datetime.now())
        logger.debug("Status updated: %s", state)
        publish_mqtt("contactor/state", state)
        return True

    def update_medians(self, powerflow_pload, powerflow_ppv):
        """
        Median calculation

        Parameters
        ----------
        powerflow_pload : float
            Current power load
        powerflow_ppv : float
            Current power from pv

        Returns
        -------
        bool
            true = success, false = fail (exception or not a deque)

        Raises
        ------
        Exception
            General exception, but most likely ValueError
        """
        try:
            if powerflow_pload is None or powerflow_ppv is None:
                raise ValueError("Input values cannot be None")

            self.pload.append(powerflow_pload)
            self.ppv.append(powerflow_ppv)

            if not self.pload or not self.ppv:
                self.pload_median = 0
                self.ppv_median = 0
                return False

            self.pload_median = statistics.median(self.pload)
            self.ppv_median = statistics.median(self.ppv)
        except Exception as e_general:
            logger.error("Error in median calculation: %s", e_general)
            return False
        else:
            logger.debug("Median power pv: %s W", round(self.ppv_median, 2))
            logger.debug("Median power load: %s W", round(self.pload_median, 2))
            #logger.debug("Power load deque: %s", list(self.pload))
            #logger.debug("Power pv deque: %s", list(self.ppv))

            if boilr.date_check and boilr.time_check and False: # DEV
                publish_mqtt("statistics/median/load", self.pload_median)
                publish_mqtt("statistics/median/pv", self.ppv_median)

            return True

boilr = Boilr()


def run():
    """
    Data gathering and processing

    Returns
    -------
    bool
        true = success, false = fail (exception)

    Raises
    ------
    ToDo
    Exception
        General exception
    """
    ## check date range
    (boilr.date_check, date_check_msg) = helper.date_check(config.SystemConfig.active_date_range)

    # date_check negative -> process shutdown sequence
    # date_check positive -> continue with time_check
    if not boilr.date_check:
        ## check if unchanged
        if boilr.date_check_prev != boilr.date_check:
            logger.info(date_check_msg)
            boilr.date_check_prev = boilr.date_check
            rpi_gpio.cleanup()

        return False
    else:
        ## check time range
        (boilr.time_check, time_check_msg) = \
            helper.time_check(config.SystemConfig.active_time_range)

        # time_check negative -> process shutdown sequence
        # time_check positive -> continue with program
        if not boilr.time_check:
            ## check if unchanged
            if boilr.time_check_prev != boilr.time_check:
                logger.info(time_check_msg)
                boilr.time_check_prev = boilr.time_check
                rpi_gpio.cleanup()

            return False
        else:
            pass

    inverter_url = config.EndpointConfig.scheme + config.EndpointConfig.ip
    logger.debug("Gathering information from endpoint at: %s", inverter_url)

    # session object with retry functionality
    session = requests.Session()
    retries = Retry(
        total=config.EndpointConfig.max_retries,
        backoff_factor=0.1,
        status_forcelist=[502, 503, 504],
        allowed_methods={'GET'},
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        response_powerflow = session.get(
            inverter_url + config.EndpointConfig.api + config.EndpointConfig.powerflow,
            timeout=config.EndpointConfig.request_timeout
        )
    except (RequestsConnectionError, Timeout, TooManyRedirects, RequestException) as exception:
        logger.warning("Error in request: %s", exception)
        boilr.update_medians(0, 0)
        return False
    except Exception as e_general:
        logger.error("Unrecoverable error in request: %s", e_general)
        boilr.update_medians(0, 0)
        daemon.daemon_stop()
        return False
    else:
        # check status code of the response
        if response_powerflow.status_code != 200:
            logger.error("Request returned status code: %s", response_powerflow.status_code)
            boilr.update_medians(0, 0)
            return False

        try:
            powerflow_site = response_powerflow.json()['Body']['Data']['Site']
        except Exception as e_general:
            logger.error("Error parsing JSON response (powerflow site): %s", e_general)
            return False
        else:
            powerflow_pgrid = powerflow_site['P_Grid'] or 0
                # + -> from grid, - -> to grid, null -> no meter enabled
            powerflow_pakku = powerflow_site['P_Akku'] or 0
                # + -> discharge, - -> charge, null -> not active
            powerflow_ppv = powerflow_site['P_PV'] or 0
                # + -> production, null -> inverter not running
            powerflow_pload = powerflow_site['P_Load'] or 0
                # - -> current load

            logger.debug("Powerflow grid: %s W", round(powerflow_pgrid, 2))
            logger.debug("Powerflow battery: %s W", round(powerflow_pakku, 2))
            logger.debug("Powerflow pv: %s W", round(powerflow_ppv, 2))
            logger.debug("Powerflow load: %s W", round(powerflow_pload, 2))

            boilr.update_medians(powerflow_pload, powerflow_ppv)

        try:
            powerflow_inverters = response_powerflow.json()['Body']['Data']['Inverters']['1']
        except Exception as e_general:
            logger.error("Error parsing JSON response (powerflow inverter): %s", e_general)
            return False
        else:
            if not powerflow_site['P_Akku'] is None:
                powerflow_soc = powerflow_inverters['SOC'] # state of charge
                logger.debug("SOC: %s %%", round(powerflow_soc, 1))
            else:
                powerflow_soc = 100
                logger.debug("SOC: Battery not active, ignoring SOC")

        ## set gpio mode
        if not rpi_gpio.gpio_mode(config.RpiConfig.rpi_channel_relay_out, "out"):
            logger.warning("Error while setting gpio mode for: output")
            logger.debug("Skipping condition evaluation")
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
            ## previous true -> condition met (instant off)
            ## previous false & timedelta between toggle -> condition met (delayed starting)
            if boilr.status_prev[0] or (not boilr.status_prev[0] and \
                (
                    boilr.status_prev[1] < datetime.now()
                    - timedelta(seconds=config.SystemConfig.start_timeout)
                )
            ):
                ## check if status unchanged
                if boilr.status_prev[0] != boilr.status[0]:
                    logger.debug(
                        "Conditions %s: contactor %s",
                        "not met" if not boilr.status[0] else "met",
                        "closed" if boilr.status[0] else "open"
                    )
                    logger.info("Status: %s", "active" if boilr.status[0] else "inactive")
                    boilr.status_prev = boilr.status

                    if not rpi_gpio.output_relay(
                        config.RpiConfig.rpi_channel_relay_out,
                        boilr.status[0]
                    ):
                        logger.warning("Error while setting gpio channel")
                        return False
                else:
                    logger.debug("Contactor unchanged - previous state: %s", boilr.status_prev[0])

        ## read relay channel
        if not rpi_gpio.gpio_mode(config.RpiConfig.rpi_channel_relay_in, "in"):
            logger.warning("Error while setting gpio mode for: input")
            return False
        elif not rpi_gpio.input_relay(config.RpiConfig.rpi_channel_relay_in):
            logger.warning("Error while reading gpio channel")
            return False
        else:
            pass

    return True


def manual_override(args):
    """
    Manually override contactor status

    Parameters
    ----------
    args : obj
        Command line arguments

    Returns
    -------
    bool
        true = success, false = fail (exception)

    Raises
    ------
    ToDo
    Exception
        General exception
    """
    try:
        if not rpi_gpio.gpio_mode(config.RpiConfig.rpi_channel_relay_out, "out") or \
            not rpi_gpio.gpio_mode(config.RpiConfig.rpi_channel_relay_in, "in") \
        :
            raise SystemError("GPIO mode failed")

        if args in {0, 1}:
            logger.debug("Manual override: contactor %s", "closed" if args == 1 else "open")
            logger.info("Status: %s (manual)", "active" if args == 1 else "inactive")
            if not rpi_gpio.output_relay(
                config.RpiConfig.rpi_channel_relay_out,
                True if args == 1 else False
            ):
                raise SystemError("GPIO channel failed")
        else:
            raise ValueError(f"Argument not in allowed set: {args}")

    except SystemError as system_exception:
        logger.error("Error while setting gpio: %s", system_exception)
        return False

    except ValueError as value_error:
        logger.error("Value error: %s", value_error)
        return False

    except Exception as e_general:
        logger.error("Error: %s", e_general)
        return False

    else:
        return True
