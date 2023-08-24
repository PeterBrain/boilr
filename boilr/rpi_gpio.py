import logging

logger = logging.getLogger(__name__)

def gpio_mode(channel, mode: str):
    """Function set GPIO mode to channel"""
    return False

def output_relay(channel, state: bool):
    """Function set GPIO channel to state"""
    return False

def input_relay(channel):
    """Function reading GPIO channel"""
    return False

def cleanup():
    """Function cleanup GPIO channel"""
    return False

try:
    import RPi.GPIO as GPIO
except RuntimeError as re:
    logger.error("While importing RPi.GPIO! This is probably because you are not executing this script on a Raspberry Pi or you need elevated privileges. %s", re)
except Exception as e_general:
    logger.error("Unexpected: Something went wrong while importing Raspberry GPIO module: %s", e_general)
else:
    def gpio_mode(channel, mode: str):
        """Function set GPIO mode to channel"""
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


    def output_relay(channel, state: bool):
        """Function set GPIO channel to state"""
        if state:
            relay = True
        else:
            relay = False

        logger.debug("Set state of gpio channel %s to '%s'", channel, state)
        GPIO.output(channel, GPIO.HIGH if relay else GPIO.LOW)
        return True


    def input_relay(channel):
        """Function reading GPIO channel"""
        logger.debug("Reading gpio channel %s", channel)
        input = GPIO.input(channel) # True or False
        return input


    def cleanup():
        """Function cleanup GPIO channel"""
        logger.debug("Reset gpio channels")
        GPIO.cleanup()
        return True

finally:
    pass
