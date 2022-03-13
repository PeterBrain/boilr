import boilr.config as config
import boilr.app as app
import boilr.rpi_gpio as rpi_gpio

import logging
import threading

logger = logging.getLogger(__name__)
stop_event = threading.Event()
class MainCtrl:
    def __init__(self, thread_continue=None, verbose=None, manual=None):
        self.thread_continue = thread_continue or True
        self.verbose = verbose or False
        self.manual = manual or False

    def main_thread_stop(signum=None, frame=None):
        thread_continue = False

mainctrl = MainCtrl()


def app_thread(stop_event):
    logger.debug("Starting app thread")

    while mainctrl.thread_continue and not stop_event.isSet():
        if mainctrl.verbose:
            logger.debug("Continuing thread...")

        app.run()
        stop_event.wait(config.SystemConfig.interval)

    logger.debug("Stopping app thread")


def main_thread(args, mainctrl):
    if hasattr(args, 'manual'):
        mainctrl.manual = True
        app.manual_override(args.manual[0])

    try:
        thread = threading.Thread(target=app_thread, args=(stop_event,))

        thread.daemon = True
        thread.start()

        while thread.is_alive():
            thread.join() # wait for the thread to complete

    except KeyboardInterrupt as ke:
        if mainctrl.verbose:
            logger.info("Interrupting... {0}".format(str(ke)))

    except Exception as e:
        if mainctrl.verbose:
            logger.error("Exception: {0}".format(str(e)))

    else:
        logger.debug("Stopping without errors")

    finally:
        stop_event.set()

        if not mainctrl.manual:
            rpi_gpio.cleanup()

        if mainctrl.verbose:
            logger.info("Verbose mode end")

        logger.info("Exiting...")
