"""Configuration module"""
import os
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import yaml

from boilr import __version__

logger = logging.getLogger(__name__)


@dataclass
class SystemConfig:
    """System configuration values"""
    prog_name: str = "boilr"  # program name
    working_directory: str = field(init=False)
    logpath: str = field(init=False)
    pidpath: str = field(init=False)
    chroot_dir: Optional[str] = None
    logging_date_format: str = "%Y-%m-%dT%H:%M:%S"
    logging_format: str = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    default_config_file: str = field(init=False)
    config_file: str = field(init=False)
    interval: int = 10  # api checking interval in seconds
    start_timeout: int = 120  # minimum time between contactor state changes in seconds
    moving_median_list_size: int = 5  # size of the array for past query values
    charge_threshold: int = 85  # minimum state of charge of the battery in %
    ppv_tolerance: int = 100  # tolerance of PV production in W
    heater_power: int = 2600  # maximum power of the heating element in W
    active_date_range: list[str] = field(default_factory=lambda: ["01-01", "31-12"])  # (day-month) ([start, end])
    active_time_range: list[str] = field(default_factory=lambda: ["00:00", "23:59"])  # (hour:minute) ([start, end])

    def __post_init__(self):
        self.working_directory = f"/var/log/{self.prog_name}"
        self.logpath = os.path.join(self.working_directory, f"{self.prog_name}.log")
        self.pidpath = os.path.join("/var/run", f"{self.prog_name}.pid")
        self.default_config_file = os.path.join("/etc", self.prog_name, "config.yaml")
        self.config_file = self.default_config_file


@dataclass
class RpiConfig:
    """GPIO configuration class"""
    rpi_channel_relay_out: int = 17  # board number 11
    rpi_channel_relay_in: int = 27  # board number 13


@dataclass
class EndpointConfig:
    """Endpoint configuration class"""
    request_timeout: int = 5  # timeout for requests in seconds
    max_retries: int = 3  # maximum number of retries for failed requests
    scheme: str = "http://"  # request scheme for api request
    host: str = "example.local"  # domain/ip-address of the inverter
    api: str = "/solar_api/v1"  # api version (inverter specific)
    # check with this URI: http://<ip-address>/solar_api/GetAPIVersion.cgi
    resource: str = "/GetPowerFlowRealtimeData.fcgi"  # resource


@dataclass
class MqttConfig:
    """MQTT broker configuration class"""
    broker_host: str = "localhost"  # domain/ip-address of the mqtt broker
    broker_port: int = 1883  # port of the broker
    topic: str = "boilr"  # root mqtt topic


# Config Object Factory
@dataclass
class Config:
    """Aggregate configuration"""
    system: SystemConfig = field(default_factory=SystemConfig)
    rpi: RpiConfig = field(default_factory=RpiConfig)
    endpoint: EndpointConfig = field(default_factory=EndpointConfig)
    mqtt: MqttConfig = field(default_factory=MqttConfig)


def initialize(args) -> Config:
    """
    Initialize configuration with precedence:
    CLI > ENV > Default YAML > Defaults
    """
    cfg = Config()

    logger.info("%s version: %s", cfg.system.prog_name, __version__)
    logger.debug(
        "Initializing configuration with log path: %s",
        cfg.system.logpath
    )

    # determine config path
    if getattr(args, "config", None):
        cfg.system.config_file = args.config
        logger.debug("Using config from CLI: %s", args.config)
    elif os.getenv("BOILR_CONFIG_PATH"):
        cfg.system.config_file = os.getenv("BOILR_CONFIG_PATH")
        logger.debug("Using config from env: %s", cfg.system.config_file)
    else:
        logger.debug("Using default config: %s", cfg.system.config_file)

    # load and apply user config if present
    user_config = _load_yaml(cfg.system.config_file)
    if user_config:
        _apply_config(cfg, user_config)

    return cfg


def _load_yaml(path: str) -> Optional[Dict[str, Any]]:
    """Load a YAML configuration file safely"""
    try:
        if not os.path.exists(path):
            logger.warning("Config file not found: %s", path)
            return None

        with open(path, "r", encoding="utf-8") as f:
            logger.debug("Reading config file: %s", path)
            return yaml.safe_load(f) or {}

    except yaml.YAMLError as e:
        logger.error("YAML parse error: %s", e)
    except PermissionError as e:
        logger.error("Permission denied reading config: %s", e)
    except Exception as e:
        logger.error("Unexpected error reading config: %s", e)
    return None


def _apply_config(cfg: Config, data: Dict[str, Any]):
    """Apply user configuration dict to config objects"""
    app = data.get("boilr", {})
    rpi = data.get("rpi", {})
    ep = data.get("endpoint", {})
    mqtt = data.get("mqtt", {})

    for k, v in app.items():
        if hasattr(cfg.system, k):
            setattr(cfg.system, k, v)
    for k, v in rpi.items():
        if hasattr(cfg.rpi, k):
            setattr(cfg.rpi, k, v)
    for k, v in ep.items():
        if hasattr(cfg.endpoint, k):
            setattr(cfg.endpoint, k, v)
    for k, v in mqtt.items():
        if hasattr(cfg.mqtt, k):
            setattr(cfg.mqtt, k, v)

    logger.debug("Configuration applied successfully")
