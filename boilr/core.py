import logging
import threading

import boilr.config as config
import boilr.app as app
import boilr.rpi_gpio as rpi_gpio

logger = logging.getLogger(__name__)
stop_event = threading.Event()

class MainCtrl:
    """Class controls"""
    def __init__(self, thread_continue=None, verbose=None, manual=None):
        self.thread_continue = thread_continue or True
        self.verbose = verbose or False
        self.manual = manual or False

    def main_thread_stop(self, signum=None, frame=None):
        """Function stopping main thread"""
        thread_continue = False

mainctrl = MainCtrl()


def app_thread(stop_event):
    """Function non blocking app thread"""
    logger.debug("Starting app thread")

    while mainctrl.thread_continue and not stop_event.isSet():
        if mainctrl.verbose:
            logger.debug("Continuing thread...")

        app.run()
        stop_event.wait(config.SystemConfig.interval)

    logger.debug("Stopping app thread")


def main_thread(args, mainctrl):
    """Function main thread"""
    if hasattr(args, 'manual'):
        mainctrl.manual = True
        app.manual_override(args.manual[0])

    try:
        thread = threading.Thread(target=app_thread, args=(stop_event,))

        thread.daemon = True
        thread.start()

        while thread.is_alive():
            thread.join() # wait for the thread to complete

    except KeyboardInterrupt as keyboard_interrupt:
        if mainctrl.verbose:
            logger.info("Interrupting... %s", keyboard_interrupt)

    except Exception as e_general:
        if mainctrl.verbose:
            logger.error("Exception: %s", e_general)

    else:
        logger.debug("Stopping without errors")

    finally:
        stop_event.set()

        if not mainctrl.manual:
            rpi_gpio.cleanup()

        if mainctrl.verbose:
            logger.info("Verbose mode end")

        logger.info("Exiting...")
