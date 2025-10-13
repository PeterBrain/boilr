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
        ctx=None,
        thread_continue=True,
        verbose=False,
        manual=False
    ):
        self.ctx = ctx
        self.thread_continue = thread_continue
        self.verbose = verbose
        self.manual = manual
        logger.debug("Initializing thread control")


    def main_thread_stop(self, signum=None, frame=None):
        """Stopping main thread"""
        self.thread_continue = False
        if self.ctx:
            self.ctx.thread_event.set()


def app_thread(ctx):
    """Non blocking app thread - called by main_thread"""
    logger.debug("Starting app thread")

    while ctx.main_ctrl.thread_continue and not ctx.thread_event.is_set():
        if not app.run(ctx):
            logger.warning("App returned False, continue with caution")

        ctx.thread_event.wait(ctx.config.system.interval)

        if ctx.main_ctrl.verbose:
            logger.debug("Continuing thread...")

    logger.debug("Stopping app thread")


def main_thread(ctx):
    """Main thread"""
    if hasattr(ctx.args, "manual"):
        ctx.main_ctrl.manual = True
        app.manual_override(ctx)  #.args.manual[0]
    else:
        thread = threading.Thread(
            target=app_thread,
            args=(ctx,)
        )
        thread.daemon = True
        thread.start()

        try:
            while thread.is_alive():
                thread.join(timeout=0.1)

        except KeyboardInterrupt:
            if ctx.main_ctrl.verbose:
                logger.info("Keyboard interrupt received")

        except RuntimeError as e_runtime:
            logger.critical("Application logic failed. Stopping daemon. %s", e_runtime)

        except Exception as e_general:
            if ctx.main_ctrl.verbose:
                logger.error("Exception: %s", e_general)

        else:
            logger.debug("Stopping without errors")

        finally:
            ctx.main_ctrl.main_thread_stop()

    if not ctx.main_ctrl.manual:
        rpi_gpio.cleanup()

    ctx.mqtt_handler.disconnect()

    if ctx.main_ctrl.verbose:
        logger.info("Verbose mode end")

    logger.info("Exiting...")
