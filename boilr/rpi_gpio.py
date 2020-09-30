import boilr.logger as logg
import logging

logger = logging.getLogger(__name__)

def gpio_mode(channel, mode):
    return False

def output_relais(channel, state):
    return False

def input_relais(channel):
    return False

def cleanup():
    return False

try:
    import RPi.GPIO as GPIO
except RuntimeError as re:
    logger.error("While importing RPi.GPIO! This is probably because you are not executing this script on a Raspberry Pi or you need elevated privileges.")
except Exception as e:
    logger.error("Unexpected: Something went wrong")
else:
    def gpio_mode(channel, mode):
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


    def output_relais(channel, state):
        if state == 0:
            logger.debug("Set state of gpio channel {0} to '{1}' (low)".format(channel, state))
            GPIO.output(channel, GPIO.LOW)
        elif state == 1:
            logger.debug("Set state of gpio channel {0} to '{1}' (high)".format(channel, state))
            GPIO.output(channel, GPIO.HIGH)
        else:
            logger.warning("GPIO state: '{0}' is not a valid state".format(state))
            return False

        return True


    def input_relais(channel):
        logger.debug("Reading gpio channel {0}".format(channel))
        input = GPIO.input(channel) # True or False
        return input


    def cleanup():
        logger.debug("Reset gpio channels")
        GPIO.cleanup()
        return True

finally:
    pass
