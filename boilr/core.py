"""Core module"""
import logging
import threading

import boilr.app as app
import boilr.rpi_gpio as rpi_gpio

logger = logging.getLogger(__name__)


class MainCtrl:
    """Main control class for thread control"""
    def __init__(
        self,
        ctx=None
    ):
        self.ctx = ctx
        logger.debug("Initializing thread control")


    def main_thread_stop(self, signum=None, frame=None):
        """Stopping main thread"""
        if not self.ctx.thread_event.is_set():
            logger.info("Shutdown requested (signal=%s)", signum)
            self.ctx.thread_event.set()


def app_thread(ctx):
    """Non blocking app thread - called by main_thread"""
    logger.debug("Starting app thread")

    while not ctx.thread_event.is_set():
        try:
            app.run(ctx)
        except Exception as e_general:
            logger.exception("Unhandled application error: %s", e_general)

        if ctx.thread_event.wait(ctx.config.system.interval):
            break

    logger.debug("Stopping app thread")


def main_thread(ctx):
    """Main thread"""
    if getattr(ctx.args, "manual", False):
        app.manual_override(ctx)
        return

    thread = threading.Thread(target=app_thread, args=(ctx,))
    #thread.daemon = True
    thread.start()

    try:
        while thread.is_alive():
            thread.join(timeout=0.1)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        ctx.main_ctrl.main_thread_stop()
        thread.join()

    except RuntimeError as e_runtime:
        logger.critical("Application logic failed. Stopping daemon. %s", e_runtime)

    except Exception as e_general:
        logger.error("Exception: %s", e_general)

    else:
        logger.debug("Stopping without errors")

    finally:
        ctx.main_ctrl.main_thread_stop()
        rpi_gpio.cleanup()
        ctx.mqtt_handler.disconnect()
        logger.info("Exiting...")
