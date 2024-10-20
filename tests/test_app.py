'''tests for app'''
from datetime import datetime
from collections import deque
from unittest.mock import patch
import statistics
import pytest
from requests.exceptions import ConnectionError
from boilr.app import Boilr, run, boilr, manual_override
import boilr.config as config


@pytest.fixture
def boilr_instance():
    """Fixture to create a fresh Boilr instance for each test"""
    config.SystemConfig.moving_median_list_size = 5
    return Boilr()


def test_boilr_initialization():
    """Test Boilr class initialization"""
    boilr = Boilr()

    # Ensure defaults are set correctly
    assert isinstance(boilr.status, tuple)
    assert isinstance(boilr.status[0], bool)
    assert isinstance(boilr.status[1], datetime)

    assert isinstance(boilr.pload, deque)
    assert len(boilr.pload) == 0
    assert boilr.pload.maxlen == config.SystemConfig.moving_median_list_size

    assert isinstance(boilr.ppv, deque)
    assert len(boilr.ppv) == 0
    assert boilr.ppv.maxlen == config.SystemConfig.moving_median_list_size


@patch('boilr.mqtt.publish_mqtt')
def test_update_medians(mock_publish):
    """Test updating medians"""
    boilr = Boilr()

    powerflow_pload = 50
    powerflow_ppv = 100
    result = boilr.update_medians(powerflow_pload, powerflow_ppv)

    assert result is True


@patch('boilr.app.logger.error')
def test_update_medians_handles_error(mock_logger_error, boilr_instance):
    """Test update_medians gracefully handles errors during calculation"""
    result = boilr_instance.update_medians(None, 200)

    assert result is False


@patch('boilr.mqtt.publish_mqtt')
def test_update_medians_calculation(mock_publish, boilr_instance):
    """Test that median calculation works correctly with valid inputs"""
    powerflow_ploads = [10, 20, 30, 40, 50]
    powerflow_ppvs = [100, 150, 200, 250, 300]

    for pload, ppv in zip(powerflow_ploads, powerflow_ppvs):
        boilr_instance.update_medians(pload, ppv)

    # Validate that the medians were calculated correctly
    assert boilr_instance.pload_median == statistics.median(powerflow_ploads)
    assert boilr_instance.ppv_median == statistics.median(powerflow_ppvs)


@patch('boilr.mqtt.publish_mqtt')
def test_update_medians_calculation_partial_data(mock_publish, boilr_instance):
    """Test update_medians with fewer than maxlen data points"""
    powerflow_ploads = [10, 20]
    powerflow_ppvs = [100, 150]

    for pload, ppv in zip(powerflow_ploads, powerflow_ppvs):
        boilr_instance.update_medians(pload, ppv)

    # Check if the medians are calculated correctly with partial data
    assert boilr_instance.pload_median == statistics.median(powerflow_ploads)
    assert boilr_instance.ppv_median == statistics.median(powerflow_ppvs)


def test_update_medians_empty_lists(boilr_instance):
    """Test update_medians with empty deque"""
    # Ensure empty deque behaves correctly
    boilr_instance.pload = deque(maxlen=5)
    boilr_instance.ppv = deque(maxlen=5)

    # Test update_medians with no data
    result = boilr_instance.update_medians(None, None)

    # Should return False as there is no data for calculation
    assert result is False
    assert boilr_instance.pload_median == 0
    assert boilr_instance.ppv_median == 0


@patch('boilr.helper.date_check')
@patch('boilr.rpi_gpio.cleanup')
def test_run_date_check_negative(mock_cleanup, mock_date_check):
    """Test run when date check is negative"""
    mock_date_check.return_value = (False, "Date not in range")
    result = run()

    assert result is False
    mock_cleanup.assert_called_once()


@patch('boilr.helper.time_check')
@patch('boilr.rpi_gpio.cleanup')
def test_run_time_check_negative(mock_cleanup, mock_time_check):
    """Test run when time check is negative"""
    boilr.date_check = True  # Simulate a positive date check
    mock_time_check.return_value = (False, "Time not in range")
    result = run()

    assert result is False
    mock_cleanup.assert_called_once()


@patch('boilr.rpi_gpio.output_relay')
@patch('boilr.rpi_gpio.gpio_mode')
def test_manual_override_valid(mock_gpio_mode, mock_output_relay):
    """Test valid manual override arguments"""
    mock_gpio_mode.return_value = True
    mock_output_relay.return_value = True

    # Test valid override (closing relay)
    result = manual_override(1)
    assert result is True

    # Test valid override (opening relay)
    result = manual_override(0)
    assert result is True


@patch('boilr.rpi_gpio.output_relay')
@patch('boilr.rpi_gpio.gpio_mode')
def test_manual_override_invalid(mock_gpio_mode, mock_output_relay):
    """Test invalid manual override argument"""
    mock_gpio_mode.return_value = True
    mock_output_relay.return_value = True

    # Test invalid argument
    result = manual_override(2)
    assert result is False


@patch('requests.Session.get')
def test_run_request_exception(mock_get):
    """Test run request exception handling"""
    mock_get.side_effect = ConnectionError("Failed to connect")
    result = run()

    assert result is False
