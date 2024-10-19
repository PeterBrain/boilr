"""Configuration module"""
import os
import logging
import yaml

from boilr._version import version as __version__

logger = logging.getLogger(__name__)

class SystemConfig():
    """System configuration class"""
    prog_name = "boilr" # program name
    working_directory = "/var/log/" + prog_name #"/var/lib/boilr/"
    logpath = os.path.join(working_directory, prog_name + ".log") #"/var/log/boilr/boilr.log"
    pidpath = os.path.join("/var/run/", prog_name + ".pid") #"/var/run/boilr.pid"
    chroot_dir = None
    logging_date_format = '%Y-%m-%dT%H:%M:%S'
    logging_format = '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s'
    default_config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    config_file = os.getenv("BOILR_CONFIG_PATH", default_config_file)

    interval = 10 # check fronius api every x seconds
    start_timeout = 120 # min time between contactor state change in seconds
    moving_median_list_size = 5 # size of the array for past request values
    charge_threshold = 85 # min battery state of charge in %
    ppv_tolerance = 100 # tolerance pv production in W
    heater_power = 2600 # power of the heating element in W (for power availability calculation)

    active_date_range = ["01-01", "31-12"] # (day-month) ([start, end])
    # e.g.: may to oct -> ["01-05", "31-10"]
    active_time_range = ["00:00", "23:59"] # (hour:minute) ([start, end])
    # e.g.: 10am to 5pm -> ["10:00", "17:00"]
    # boilr is active after charge_threshold is exceeded
    # boilr is inactive before the battery is discharged

class RpiConfig():
    """GPIO configuration class"""
    rpi_channel_relay_out = 17 # board number 11
    rpi_channel_relay_in = 27 # board number 13

class EndpointConfig():
    """Endpoint configuration class"""
    request_timeout = 5 # timeout for requests in seconds
    max_retries = 3 # maximum retries for requests
    scheme = "http://" # scheme
    ip = "example.local" # domain/ip address of the inverter
    api = "/solar_api/v1" # api version (inverter specific)
        # check with this URI: http://<ip-address>/solar_api/GetAPIVersion.cgi
    powerflow = "/GetPowerFlowRealtimeData.fcgi" # resource

class MqttConfig():
    """MQTT broker configuration class"""
    broker_ip = "localhost" # ip address of the mqtt broker
    broker_port = 1883 # port of the broker
    topic = "boilr" # root mqtt topic


def initialize():
    """Initialize configuration"""
    logger.info("%s version: %s", SystemConfig.prog_name, __version__)
    logger.info("Config initialized with log path: %s", SystemConfig.logpath)
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
        with open(SystemConfig.config_file, "r", encoding="utf-8") as yaml_file:
            user_config = yaml.safe_load(yaml_file)
            logger.debug("Parsed configuration file: %s", yaml_file.name)

    except FileNotFoundError as file_not_found:
        logger.error("File not found: %s", file_not_found)
        logger.info("Continue with defaults")

    except Exception as e_general:
        logger.error("Unrecoverable error while importing user configuration: %s", e_general)
        logger.info("Continue with defaults")

    else:
        logger.debug("Applying configuration")

        app_config = user_config["boilr"]
        rpi_config = user_config["rpi"]
        rest_config = user_config["endpoint"]
        mqtt_config = user_config["mqtt"]

        SystemConfig.interval = app_config['interval']
        SystemConfig.start_timeout = app_config['start_timeout']
        SystemConfig.moving_median_list_size = app_config['moving_median_list_size']
        SystemConfig.charge_threshold = app_config['charge_threshold']
        SystemConfig.ppv_tolerance = app_config['ppv_tolerance']
        SystemConfig.heater_power = app_config['heater_power']
        SystemConfig.active_date_range = app_config['active_date_range']
        SystemConfig.active_time_range = app_config['active_time_range']

        RpiConfig.rpi_channel_relay_out = rpi_config['rpi_channel_relay_out']
        RpiConfig.rpi_channel_relay_in = rpi_config['rpi_channel_relay_in']

        EndpointConfig.request_timeout = rest_config['request_timeout']
        EndpointConfig.max_retries = rest_config['max_retries']
        EndpointConfig.scheme = rest_config['scheme']
        EndpointConfig.ip = rest_config['ip']
        EndpointConfig.api = rest_config['api']
        EndpointConfig.powerflow = rest_config['powerflow']

        MqttConfig.broker_ip = mqtt_config['broker_ip']
        MqttConfig.broker_port = mqtt_config['broker_port']
        MqttConfig.topic = mqtt_config['topic']

        logger.debug("Finished applying configuration")

    finally:
        pass
