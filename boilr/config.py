"""Configuration module"""
import os
import logging
import yaml

from boilr import __version__

logger = logging.getLogger(__name__)


class SystemConfig():
    """System configuration class"""
    prog_name = "boilr"  # program name
    working_directory = "/var/log/" + prog_name  # "/var/log/boilr"
    logpath = os.path.join(working_directory, prog_name + ".log")  # "/var/log/boilr/boilr.log"
    pidpath = os.path.join("/var/run", prog_name + ".pid")  # "/var/run/boilr.pid"
    chroot_dir = None
    logging_date_format = '%Y-%m-%dT%H:%M:%S'
    logging_format = '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s'
    default_config_file = os.path.join("/etc", prog_name, "config.yaml")  # "/etc/boilr/config.yaml"
    config_file = default_config_file

    interval = 10  # api checking interval in seconds
    start_timeout = 120  # minimum time between contactor state changes in seconds
    moving_median_list_size = 5  # size of the array for past query values
    charge_threshold = 85  # minimum state of charge of the battery in %
    ppv_tolerance = 100  # tolerance of PV production in W
    heater_power = 2600  # maximum power of the heating element in W

    active_date_range = ["01-01", "31-12"]  # (day-month) ([start, end])
    active_time_range = ["00:00", "23:59"]  # (hour:minute) ([start, end])


class RpiConfig():
    """GPIO configuration class"""
    rpi_channel_relay_out = 17  # board number 11
    rpi_channel_relay_in = 27  # board number 13


class EndpointConfig():
    """Endpoint configuration class"""
    request_timeout = 5  # timeout for requests in seconds
    max_retries = 3  # maximum number of retries for failed requests
    scheme = "http://"  # request scheme for api request
    host = "example.local"  # domain/ip-address of the inverter
    api = "/solar_api/v1"  # api version (inverter specific)
    # check with this URI: http://<ip-address>/solar_api/GetAPIVersion.cgi
    resource = "/GetPowerFlowRealtimeData.fcgi"  # resource


class MqttConfig():
    """MQTT broker configuration class"""
    broker_host = "localhost"  # domain/ip-address of the mqtt broker
    broker_port = 1883  # port of the broker
    topic = "boilr"  # root mqtt topic


def initialize(args):
    """
    Initialize configuration

    Parameters
    ----------
    args : obj
        Command line arguments
    """
    logger.info("%s version: %s", SystemConfig.prog_name, __version__)
    logger.debug("Config initialized with log path: %s", SystemConfig.logpath)

    if args.config:
        SystemConfig.config_file = args.config
        logger.debug("Command line config: %s", args.config)
    elif os.getenv("BOILR_CONFIG_PATH"):
        # logger.debug("Environment variables: %s", os.environ)
        config_path = os.getenv("BOILR_CONFIG_PATH")
        logger.debug("Found BOILR_CONFIG_PATH in env: %s", config_path)
        SystemConfig.config_file = config_path
    else:
        logger.debug(
            "Neither command line config nor environment variable is passed"
        )

    logger.info("Using configuration file: %s", SystemConfig.config_file)
    import_config()


def import_config():
    """
    Import user configuration file

    Raises
    ------
    ToDo
    Exception
        General exception
    """
    try:
        if not os.path.exists(SystemConfig.config_file):
            raise FileNotFoundError(f"Configuration file not found at {SystemConfig.config_file}")

        with open(SystemConfig.config_file, "r", encoding="utf-8") as yaml_file:
            user_config = yaml.safe_load(yaml_file)
            logger.debug("Parsed configuration file")
            apply_config(user_config)

    except FileNotFoundError as file_not_found:
        logger.error("Configuration file not found: %s", file_not_found)
        logger.info("Continuing with default settings")

    except yaml.YAMLError as yaml_error:
        logger.error("Error parsing YAML configuration: %s", yaml_error)
        logger.info("Please check the syntax of your configuration file")
        logger.info("Continuing with default settings")

    except PermissionError as permission_error:
        logger.error("Permission denied for configuration file: %s", permission_error)
        logger.info("Ensure the application has access to the configuration file")
        logger.info("Continuing with default settings")

    except Exception as general_error:
        logger.error("Unexpected error loading configuration: %s", general_error)
        logger.info("Continuing with default settings")


def apply_config(user_config):
    """
    Apply configuration to system settings

    Parameters
    ----------
    user_config : obj
    """
    try:
        app_config = user_config.get("boilr", {})
        rpi_config = user_config.get("rpi", {})
        rest_config = user_config.get("endpoint", {})
        mqtt_config = user_config.get("mqtt", {})

        SystemConfig.interval = app_config.get('interval', SystemConfig.interval)
        SystemConfig.start_timeout = app_config.get('start_timeout', SystemConfig.start_timeout)
        SystemConfig.moving_median_list_size = app_config.get('moving_median_list_size', SystemConfig.moving_median_list_size)
        SystemConfig.charge_threshold = app_config.get('charge_threshold', SystemConfig.charge_threshold)
        SystemConfig.ppv_tolerance = app_config.get('ppv_tolerance', SystemConfig.ppv_tolerance)
        SystemConfig.heater_power = app_config.get('heater_power', SystemConfig.heater_power)
        SystemConfig.active_date_range = app_config.get('active_date_range', SystemConfig.active_date_range)
        SystemConfig.active_time_range = app_config.get('active_time_range', SystemConfig.active_time_range)

        RpiConfig.rpi_channel_relay_out = rpi_config.get('rpi_channel_relay_out', RpiConfig.rpi_channel_relay_out)
        RpiConfig.rpi_channel_relay_in = rpi_config.get('rpi_channel_relay_in', RpiConfig.rpi_channel_relay_in)

        EndpointConfig.request_timeout = rest_config.get('request_timeout', EndpointConfig.request_timeout)
        EndpointConfig.max_retries = rest_config.get('max_retries', EndpointConfig.max_retries)
        EndpointConfig.scheme = rest_config.get('scheme', EndpointConfig.scheme)
        EndpointConfig.host = rest_config.get('host', EndpointConfig.host)
        EndpointConfig.api = rest_config.get('api', EndpointConfig.api)
        EndpointConfig.resource = rest_config.get('resource', EndpointConfig.resource)

        MqttConfig.broker_host = mqtt_config.get('broker_host', MqttConfig.broker_host)
        MqttConfig.broker_port = mqtt_config.get('broker_port', MqttConfig.broker_port)
        MqttConfig.topic = mqtt_config.get('topic', MqttConfig.topic)

        logger.debug("Configuration applied successfully")

    except KeyError as key_error:
        logger.warning("Missing key in configuration file: %s", key_error)
        logger.info("Ensure all required keys are present in the configuration")
        logger.info("Continuing with partial defaults")
