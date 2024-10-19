"""Core module"""
import logging
import threading

import boilr.config as config
import boilr.app as app
import boilr.rpi_gpio as rpi_gpio

logger = logging.getLogger(__name__)
thread_event = threading.Event()

class MainCtrl:
    """Main control class for thread control"""
    def __init__(self, thread_continue=None, verbose=None, manual=None):
        self.thread_continue = thread_continue if thread_continue is not None else True
        self.verbose = verbose if verbose is not None else False
        self.manual = manual if manual is not None else False

    def main_thread_stop(self, signum=None, frame=None):
        """Stopping main thread"""
        self.thread_continue = False

mainctrl = MainCtrl()


def app_thread(thread_stop_event, mainctrl_instance):
    """
    Non blocking app thread - called by main_thread

    Parameters
    ----------
    thread_stop_event :
        Internal flag for stop event
    mainctrl_instance :
        Instance of the MainCtrl class
    """
    logger.debug("Starting app thread")

    while mainctrl_instance.thread_continue and not thread_stop_event.is_set():
        if mainctrl_instance.verbose:
            logger.debug("Continuing thread...")

        app.run()
        thread_stop_event.wait(config.SystemConfig.interval)

    logger.debug("Stopping app thread")


def main_thread(args, mainctrl_instance):
    """
    Main thread

    Parameters
    ----------
    args : obj
        Command line arguments
    mainctrl_instance :
        Instance of MainCtrl class

    Raises
    ------
    ToDo
    Exception
        General exception
    """
    if hasattr(args, 'manual'):
        mainctrl_instance.manual = True
        app.manual_override(args.manual[0])

    thread = threading.Thread(target=app_thread, args=(thread_event, mainctrl_instance,))
    thread.daemon = True
    thread.start()

    try:
        while True:
            if not thread.is_alive():
                break

            thread.join(timeout=0.1)

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
