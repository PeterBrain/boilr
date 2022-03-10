import logging

logger = logging.getLogger(__name__)

def gpio_mode(channel, mode: str):
    return False

def output_relay(channel, state: bool):
    return False

def input_relay(channel):
    return False

def cleanup():
    return False

try:
    import RPi.GPIO as GPIO
except RuntimeError as re:
    logger.error("While importing RPi.GPIO! This is probably because you are not executing this script on a Raspberry Pi or you need elevated privileges.")
except Exception as e:
    logger.error("Unexpected: Something went wrong while importing Raspberry GPIO module")
else:
    def gpio_mode(channel, mode: str):
        logger.debug("Define gpio channel {0} and assign mode '{1}'".format(channel, mode))
        GPIO.setmode(GPIO.BCM) # GPIO number (GPIO.BOARD for board number)

        if mode == "out":
            GPIO.setup(channel, GPIO.OUT)
        elif mode == "in":
            GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP) #pull_up_down=GPIO.PUD_DOWN
        else:
            logger.warning("GPIO mode: '{0}' is not valid".format(mode))
            return False

        return True


    def output_relay(channel, state: bool):
        if state:
            relay = True
        else:
            relay = False

        logger.debug("Set state of gpio channel {0} to '{1}'".format(channel, state))
        GPIO.output(channel, GPIO.HIGH if relay else GPIO.LOW)
        return True


    def input_relay(channel):
        logger.debug("Reading gpio channel {0}".format(channel))
        input = GPIO.input(channel) # True or False
        return input


    def cleanup():
        logger.debug("Reset gpio channels")
        GPIO.cleanup()
        return True

finally:
    pass
