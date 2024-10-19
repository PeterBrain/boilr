"""GPIO module"""
import logging

logger = logging.getLogger(__name__)

def gpio_mode(channel: int, mode: str):
    """Function set GPIO mode for channel"""
    return False

def output_relay(channel: int, state: bool):
    """Function set GPIO channel to state"""
    return False

def input_relay(channel: int):
    """Function reading GPIO channel"""
    return False

def cleanup():
    """Function cleanup GPIO channel"""
    return False

try:
    import RPi.GPIO as GPIO
except ImportError as ie:
    logger.debug("Unable to import RPi.GPIO module: %s", ie)
except RuntimeError as re:
    logger.error(
        "While importing RPi.GPIO! This is probably because you are not executing \
            this script on a Raspberry Pi or you need elevated privileges. %s",
        re
    )
except Exception as e_general:
    logger.error(
        "Unexpected: Something went wrong while importing GPIO module: %s",
        e_general
    )
else:
    def gpio_mode(channel: int, mode: str):
        """
        Set GPIO mode for channel

        Parameters
        ----------
        channel : int
            GPIO channel on the hardware
        mode : str
            input or output

        Returns
        -------
        bool
            true = success; false = fail
        """
        logger.debug("Define gpio channel %s and assign mode '%s'", channel, mode)
        GPIO.setmode(GPIO.BCM) # GPIO number (GPIO.BOARD for board number)

        if mode == "out":
            GPIO.setup(channel, GPIO.OUT)
        elif mode == "in":
            GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP) #pull_up_down=GPIO.PUD_DOWN
        else:
            logger.warning("GPIO mode: '%s' is not valid", mode)
            return False

        return True


    def output_relay(channel: int, state: bool):
        """
        Set GPIO channel to state

        Parameters
        ----------
        channel : int
            GPIO channel on the hardware
        state : bool
            channel hight or low

        Returns
        -------
        bool
            true = success; false = fail
        """
        if state:
            relay = True
        else:
            relay = False

        logger.debug("Set state of gpio channel %s to '%s'", channel, state)
        GPIO.output(channel, GPIO.HIGH if relay else GPIO.LOW)
        return True


    def input_relay(channel: int):
        """
        Reading GPIO channel

        Parameters
        ----------
        channel : int
            GPIO channel on the hardware

        Returns
        -------
        bool
            Value from input channel (Relay)
        """
        logger.debug("Reading gpio channel %s", channel)
        relay_input = GPIO.input(channel) # True or False
        return relay_input


    def cleanup():
        """
        Cleanup GPIO channel

        Returns
        -------
        bool
            true = always true
        """
        logger.debug("Reset gpio channels")
        GPIO.cleanup()
        return True

finally:
    pass
