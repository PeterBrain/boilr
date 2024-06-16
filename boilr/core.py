"""application core"""
import logging
import threading

import boilr.config as config
import boilr.app as app
import boilr.rpi_gpio as rpi_gpio

logger = logging.getLogger(__name__)
thread_event = threading.Event()

class MainCtrl:
    """Class thread control"""
    def __init__(self, thread_continue=None, verbose=None, manual=None):
        self.thread_continue = thread_continue or True
        self.verbose = verbose or False
        self.manual = manual or False

    def main_thread_stop(self, signum=None, frame=None):
        """Function stopping main thread"""
        #thread_event.set()
        self.thread_continue = False

mainctrl = MainCtrl()


def app_thread(thread_stop_event, mainctrl_instance):
    """Function non blocking app thread - called by main_thread"""
    logger.debug("Starting app thread")

    while mainctrl_instance.thread_continue and not thread_stop_event.isSet():
        if mainctrl_instance.verbose:
            logger.debug("Continuing thread...")

        app.run()
        thread_stop_event.wait(config.SystemConfig.interval)

    logger.debug("Stopping app thread")


def main_thread(args, mainctrl_instance):
    """Function main thread"""
    if hasattr(args, 'manual'):
        mainctrl_instance.manual = True
        app.manual_override(args.manual[0])

    try:
        thread = threading.Thread(target=app_thread, args=(thread_event, mainctrl_instance,))

        thread.daemon = True
        thread.start()

        while thread.is_alive():
            thread.join() # wait for the thread to complete

    except KeyboardInterrupt as keyboard_interrupt:
        if mainctrl_instance.verbose:
            logger.info("Interrupting... %s", keyboard_interrupt)

    except Exception as e_general:
        if mainctrl_instance.verbose:
            logger.error("Exception: %s", e_general)

    else:
        logger.debug("Stopping without errors")

    finally:
        thread_event.set()

        if not mainctrl_instance.manual:
            rpi_gpio.cleanup()

        if mainctrl_instance.verbose:
            logger.info("Verbose mode end")

        logger.info("Exiting...")
