"""App module"""
import logging
import statistics
from datetime import datetime, timedelta
from typing import List
from collections import deque
from urllib3.util import Retry
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import (
    ConnectionError as RequestsConnectionError,
    Timeout,
    TooManyRedirects,
    RequestException
)

import boilr.daemon as daemon
import boilr.helper as helper
import boilr.rpi_gpio as rpi_gpio
from boilr.mqtt import publish_mqtt

logger = logging.getLogger(__name__)


class Boilr:
    """
    Boilr class

    Holds all status variables and handles state logic
    """
    def __init__(
        self,
        ctx,
        status=None,
        status_prev=None,
        pload: List[float] = None,
        ppv: List[float] = None
    ):
        self.ctx = ctx
        self.logger = logger
        self.config = ctx.config

        self.status = (status or False, datetime.now())
        self.status_prev = (status_prev or False, datetime.now())
        self.date_check = True
        self.date_check_prev = True
        self.time_check = True
        self.time_check_prev = True

        self.pload = deque(maxlen=self.config.system.moving_median_list_size)
        self.ppv = deque(maxlen=self.config.system.moving_median_list_size)
        self.pload_median = 0
        self.ppv_median = 0


    def update_status(self, state: bool):
        """Update contactor status"""
        self.status = (state, datetime.now())
        self.logger.debug("Status updated: %s", state)
        publish_mqtt("contactor/state", state)
        return True


    def update_medians(self, powerflow_pload, powerflow_ppv):
        """Median calculation"""
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
            self.logger.error("Error in median calculation: %s", e_general)
            return False
        else:
            self.logger.debug("Median power pv: %s W", round(self.ppv_median, 2))
            self.logger.debug("Median power load: %s W", round(self.pload_median, 2))
            #logger.debug("Power load deque: %s", list(self.pload))
            #logger.debug("Power pv deque: %s", list(self.ppv))

            #if self.date_check and self.time_check:  # DEV
            #    publish_mqtt("statistics/median/load", self.pload_median)
            #    publish_mqtt("statistics/median/pv", self.ppv_median)

            return True


def run(ctx):
    """Data gathering and control logic"""
    boilr_instance = ctx.boilr
    config = ctx.config

    # check date range
    (boilr_instance.date_check, date_check_msg) = \
        helper.date_check(config.system.active_date_range)

    # date_check negative -> process shutdown sequence
    # date_check positive -> continue with time_check
    if not boilr_instance.date_check:
        # check if unchanged
        if boilr_instance.date_check_prev != boilr_instance.date_check:
            logger.info(date_check_msg)
            boilr_instance.date_check_prev = boilr_instance.date_check
            rpi_gpio.cleanup()

        return False
    else:
        # check time range
        (boilr_instance.time_check, time_check_msg) = \
            helper.time_check(config.system.active_time_range)

        # time_check negative -> process shutdown sequence
        # time_check positive -> continue with program
        if not boilr_instance.time_check:
            # check if unchanged
            if boilr_instance.time_check_prev != boilr_instance.time_check:
                logger.info(time_check_msg)
                boilr_instance.time_check_prev = boilr_instance.time_check
                rpi_gpio.cleanup()

            return False
        else:
            pass

    # Check date/time ranges
    # boilr_instance.date_check, _ = helper.date_check(config.SystemConfig.active_date_range)
    # boilr_instance.time_check, _ = helper.time_check(config.SystemConfig.active_time_range)

    # If outside allowed ranges, clean up GPIO
    #if not (boilr_instance.date_check and boilr_instance.time_check):
    #    rpi_gpio.cleanup()
    #    return False

    inverter_url = f"{config.endpoint.scheme}{config.endpoint.host}"
    logger.debug("Gathering information from endpoint at: %s", inverter_url)

    # session object with retry functionality
    session = requests.Session()
    retries = Retry(
        total=config.endpoint.max_retries,
        backoff_factor=0.1,
        status_forcelist=[502, 503, 504],
        allowed_methods={"GET"},
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        response_powerflow = session.get(
            f"{inverter_url}{config.endpoint.api}{config.endpoint.resource}",
            timeout=config.endpoint.request_timeout,
        )
        #response.raise_for_status()
    except (RequestsConnectionError, Timeout, TooManyRedirects,
            RequestException) as exception:
        logger.warning("Error in request: %s", exception)
        boilr_instance.update_medians(0, 0)
        return False
    except Exception as e_general:
        logger.error("Unrecoverable error in request: %s", e_general)
        daemon.daemon_stop(ctx)
        boilr_instance.update_medians(0, 0)
        return False
    else:
        if response_powerflow.status_code != 200:
            logger.error(
                "Request returned status code: %s",
                response_powerflow.status_code
            )
            boilr_instance.update_medians(0, 0)
            return False

        try:
            response_powerflow_data = response_powerflow.json()["Body"]["Data"]
            powerflow_site = response_powerflow_data["Site"]
            powerflow_inverters = response_powerflow_data["Inverters"]["1"]
        except Exception as e_general:
            logger.error("Error parsing JSON response (powerflow): %s", e_general)
            return False

        powerflow_pgrid = powerflow_site["P_Grid"] or 0
        # + -> from grid, - -> to grid, null -> no meter enabled
        powerflow_pakku = powerflow_site["P_Akku"] or 0
        # + -> discharge, - -> charge, null -> not active
        powerflow_ppv = powerflow_site["P_PV"] or 0
        # + -> production, null -> inverter not running
        powerflow_pload = powerflow_site["P_Load"] or 0
        # - -> current load

        logger.debug("Powerflow grid: %s W", round(powerflow_pgrid, 2))
        logger.debug("Powerflow battery: %s W", round(powerflow_pakku, 2))
        logger.debug("Powerflow pv: %s W", round(powerflow_ppv, 2))
        logger.debug("Powerflow load: %s W", round(powerflow_pload, 2))

        boilr_instance.update_medians(powerflow_pload, powerflow_ppv)
        #boilr_instance.update_medians(powerflow_site.get("P_Load", 0), powerflow_site.get("P_PV", 0))

        #powerflow_soc = powerflow_inverters.get("SOC", 100)
        if powerflow_site["P_Akku"] is not None:
            powerflow_soc = powerflow_inverters["SOC"]  # state of charge
            logger.debug("SOC: %s %%", round(powerflow_soc, 1))
        else:
            powerflow_soc = 100
            logger.debug("SOC: Battery not active, ignoring SOC")

        # set gpio mode
        if not rpi_gpio.gpio_mode(config.rpi.rpi_channel_relay_out, "out"):
            logger.warning("Error while setting gpio mode for: output")
            logger.debug("Skipping condition evaluation")
            return False
        else:
            logger.debug("Checking conditions")

            should_switch = (
                powerflow_soc >= config.system.charge_threshold and
                # soc over threshold
                boilr_instance.ppv_median > (
                    (config.system.heater_power
                        if not boilr_instance.status_prev[0] else 0)
                    + abs(boilr_instance.pload_median)
                    - config.system.ppv_tolerance
                )
                # median pv production is over
                # median load + expected load with tolerance
            )
            boilr_instance.update_status(should_switch)

            # check start timeout (instant off, delayed starting)
            # previous true -> condition met (instant off)
            # previous false & timedelta between toggle
            #   -> condition met (delayed starting)

            # start timeout checks combined
            # if (boilr_instance.status_prev[0] != boilr_instance.status[0] and
            #    (boilr_instance.status_prev[0] or
            #        (datetime.now() - boilr_instance.status_prev[1]).total_seconds() > config.SystemConfig.start_timeout)):
            if boilr_instance.status_prev[0] or \
                (not boilr_instance.status_prev[0] and
                    (boilr_instance.status_prev[1] < datetime.now()
                        - timedelta(seconds=config.SystemConfig.start_timeout))):
                # check if status unchanged
                if boilr_instance.status_prev[0] != boilr_instance.status[0]:
                    logger.debug(
                        "Conditions %s: contactor %s",
                        "not met" if not boilr_instance.status[0] else "met",
                        "closed" if boilr_instance.status[0] else "open"
                    )
                    logger.info(
                        "Status: %s",
                        "active" if boilr_instance.status[0] else "inactive"
                    )
                    boilr_instance.status_prev = boilr_instance.status

                    if not rpi_gpio.output_relay(
                        config.RpiConfig.rpi_channel_relay_out,
                        boilr_instance.status[0]
                    ):
                        logger.warning("Error while setting gpio channel")
                        return False
                else:
                    logger.debug(
                        "Contactor unchanged - previous state: %s",
                        boilr_instance.status_prev[0]
                    )

        # read relay channel
        if not rpi_gpio.gpio_mode(config.RpiConfig.rpi_channel_relay_in, "in"):
            logger.warning("Error while setting gpio mode for: input")
            return False
        elif not rpi_gpio.input_relay(config.RpiConfig.rpi_channel_relay_in):
            logger.warning("Error while reading gpio channel")
            return False
        else:
            pass

    return True


def manual_override(ctx):
    """Manually override contactor status"""
    try:
        if (not rpi_gpio.gpio_mode(ctx.config.rpi.rpi_channel_relay_out, "out") or \
            not rpi_gpio.gpio_mode(ctx.config.rpi.rpi_channel_relay_in, "in")):
            raise SystemError("GPIO mode failed")

        if ctx.args in {0, 1}:
            logger.debug(
                "Manual override: contactor %s",
                "closed" if ctx.args == 1 else "open"
            )
            logger.info(
                "Status: %s (manual)",
                "active" if ctx.args == 1 else "inactive"
            )
            if not rpi_gpio.output_relay(
                ctx.config.rpi.rpi_channel_relay_out,
                True if ctx.args == 1 else False
            ):
                raise SystemError("GPIO channel failed")
        else:
            raise ValueError(f"Argument not in allowed set: {ctx.args}")

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
