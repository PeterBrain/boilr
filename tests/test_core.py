"""Tests for core"""
import unittest
from unittest.mock import patch
import threading
import logging
from boilr.core import MainCtrl, app_thread

logger = logging.getLogger(__name__)


class TestMainCtrl(unittest.TestCase):
    """Test class for MainCtrl"""

    def test_mainctrl_initialization(self):
        """Test MainCtrl initialization with default values"""
        ctrl = MainCtrl()
        self.assertTrue(ctrl.thread_continue)
        self.assertFalse(ctrl.verbose)
        self.assertFalse(ctrl.manual)

    def test_mainctrl_custom_initialization(self):
        """Test MainCtrl initialization with custom values"""
        ctrl = MainCtrl(thread_continue=False, verbose=True, manual=True)
        self.assertFalse(ctrl.thread_continue)
        self.assertTrue(ctrl.verbose)
        self.assertTrue(ctrl.manual)

    def test_mainctrl_main_thread_stop(self):
        """Test stopping the main thread"""
        ctrl = MainCtrl()
        ctrl.main_thread_stop()
        self.assertFalse(ctrl.thread_continue)


class TestAppThread(unittest.TestCase):
    """Test class for app_thread"""

    @patch('boilr.app.run')
    @patch('boilr.config.SystemConfig')
    def test_app_thread_runs_correctly(self, mock_config, mock_app_run):
        """Test app_thread runs correctly with mock app.run()"""
        mock_config.interval = 0.1  # Set small interval for quick testing
        thread_stop_event = threading.Event()
        mainctrl = MainCtrl(thread_continue=True)

        # Run the app_thread for a short time
        with patch('boilr.core.logger') as mock_logger:
            thread = threading.Thread(
                target=app_thread,
                args=(thread_stop_event, mainctrl)
            )
            thread.start()
            thread_stop_event.set()  # Stop the thread
            thread.join()

            mock_app_run.assert_called()  # Check if app.run() was called
            mock_logger.debug.assert_any_call("Starting app thread")
            mock_logger.debug.assert_any_call("Stopping app thread")

    @patch('boilr.config.SystemConfig')
    def test_app_thread_stops_when_thread_event_set(self, mock_config):
        """Test app_thread stops when thread_event is set"""
        mock_config.interval = 0.1
        thread_stop_event = threading.Event()
        mainctrl = MainCtrl(thread_continue=True)

        with patch('boilr.core.logger') as mock_logger:
            thread = threading.Thread(
                target=app_thread,
                args=(thread_stop_event, mainctrl)
            )
            thread.start()
            thread_stop_event.set()  # Stop the thread
            thread.join()

            mock_logger.debug.assert_any_call("Stopping app thread")

    @patch('boilr.app.run')
    @patch('boilr.config.SystemConfig')
    def test_app_thread_stops_when_thread_continue_is_false(
        self,
        mock_config,
        mock_app_run
    ):
        """Test app_thread stops when thread_continue is set to False"""
        mock_config.interval = 0.1
        thread_stop_event = threading.Event()
        mainctrl = MainCtrl(thread_continue=False)

        with patch('boilr.core.logger') as mock_logger:
            thread = threading.Thread(
                target=app_thread,
                args=(thread_stop_event, mainctrl)
            )
            thread.start()
            thread_stop_event.set()  # Stop the thread
            thread.join()

            mock_app_run.assert_not_called()  # app.run() was never called
            mock_logger.debug.assert_any_call("Stopping app thread")


if __name__ == '__main__':
    unittest.main()
