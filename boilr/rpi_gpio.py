import boilr.logger as logg
import logging

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO

except RuntimeError:
    logger.error("Error importing RPi.GPIO! This is probably because you are not executing this script on a Raspberry Pi or you need elevated privileges.")

    def gpio_relais(pin):
        return False

    def output_relais(pin, state):
        return False

    def cleanup():
        return False

except:
    logger.error("Unexpected: Something went wrong")

    def gpio_relais(pin):
        return False

    def output_relais(pin, state):
        return False

    def cleanup():
        return False

else:
    def gpio_relais(pin):
        logger.debug("define gpio pin and assign mode")
        GPIO.setmode(GPIO.BCM) # GPIO number (GPIO.BOARD for board number)
        GPIO.setup(pin, GPIO.OUT) # GPIO mode
        return True


    def output_relais(pin, state):
        if state == 0:
            logger.debug("set state of gpio pin to low")
            GPIO.output(pin, GPIO.LOW)
        elif state == 1:
            logger.debug("set state of gpio pin to high")
            GPIO.output(pin, GPIO.HIGH)
        else:
            logger.warning("GPIO state: " + str(state) + " is not a valid state")
            return False
        return True


    def cleanup():
        logger.debug("reset gpio pins")
        GPIO.cleanup()
        return True

finally:
    pass
