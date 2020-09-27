import boilr.logger as logg
import logging

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO

    def gpio_relais(pin):
        GPIO.setmode(GPIO.BCM) # GPIO number (GPIO.BOARD for board number)
        GPIO.setup(pin, GPIO.OUT) # GPIO mode
        return True


    def output_relais(pin, state):
        logger.info("output")
        if state == 0:
            GPIO.output(pin, GPIO.LOW)
        elif state == 1:
            GPIO.output(pin, GPIO.HIGH)
        else:
            logger.info("not a valid state")
            return False
        return True


    def cleanup():
        GPIO.cleanup()
        return True

except RuntimeError:
    logger.error("Error importing RPi.GPIO! This is probably because you are not executing this script on a Raspberry Pi or you need elevated privileges.")

    def gpio_relais(pin):
        return False

    def output_relais(pin, state):
        return False

    def cleanup():
        return False

except:
    logger.error("Something went wrong")

    def gpio_relais(pin):
        return False

    def output_relais(pin, state):
        return False

    def cleanup():
        return False
