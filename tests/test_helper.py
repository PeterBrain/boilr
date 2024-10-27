"""Tests for helper"""
from datetime import datetime
from unittest.mock import patch
import pytest
from boilr.helper import date_check, time_check


@pytest.fixture
def mock_datetime_now():
    """Fixture to mock datetime.now() to return a specific date."""
    with patch('boilr.helper.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 6, 15, 15, 30)
        # Mocking to 15th June 2024 15:30 (3:30 pm)
        mock_datetime.strptime = datetime.strptime
        yield mock_datetime


def test_date_check_within_range(mock_datetime_now):
    """Test date within active range"""
    active_date_range = ["01-01", "31-12"]  # Full year range
    result, msg = date_check(active_date_range)
    assert result is True
    assert msg == "Date within active range"


def test_date_check_out_of_range(mock_datetime_now):
    """Test date out of active range"""
    active_date_range = ["01-07", "31-12"]  # Only July to December
    result, msg = date_check(active_date_range)
    assert result is False
    assert "Date is not in active range" in msg


def test_time_check_within_range(mock_datetime_now):
    """Test time within active range"""
    active_time_range = ["00:00", "23:59"]  # Full day range
    result, msg = time_check(active_time_range)
    assert result is True
    assert msg == "Time within active range"


def test_time_check_out_of_range(mock_datetime_now):
    """Test time out of active range"""
    active_time_range = ["16:00", "17:00"]  # 4 PM to 5 PM
    result, msg = time_check(active_time_range)
    assert result is False
    assert "Time is not in active range" in msg
