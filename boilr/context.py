"""Context module"""
from dataclasses import dataclass, field
import logging
import threading

from boilr.config import Config
from boilr.core import MainCtrl
from boilr.app import Boilr
from boilr.mqtt import MQTTHandler


@dataclass
class Context:
    """Context class"""
    args: object
    config: Config
    logger: logging.Logger = None
    console_handler: logging.Handler = None
    file_handler: logging.Handler = None
    main_ctrl: MainCtrl = None
    boilr: Boilr = None
    mqtt_handler: MQTTHandler = None
    thread_event: threading.Event = field(default_factory=threading.Event)
