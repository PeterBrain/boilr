"""Tests for __main__"""
from unittest import mock
import pytest
from boilr.__main__ import main


@pytest.fixture
def mock_parser():
    """Fixture to mock the parser and logging setup"""
    with mock.patch('boilr.argparse.parser') as parser_mock:
        yield parser_mock


@pytest.fixture
def mock_logger_setup():
    """Fixture to mock the logging setup function"""
    with mock.patch('boilr.logger.setup_logging') as mock_setup_logging:
        yield mock_setup_logging


@pytest.fixture
def mock_logger():
    """Fixture to capture logs for verification"""
    with mock.patch('logging.getLogger') as mock_get_logger:
        mock_logger_instance = mock.Mock()
        mock_get_logger.return_value = mock_logger_instance
        yield mock_logger_instance


def test_main_with_valid_command(mock_parser, mock_logger_setup, mock_logger):
    """Test main with a valid command that has a callback"""
    # Mocking parsed arguments with a callback
    mock_callback = mock.Mock()
    mock_parser.parse_args.return_value = mock.Mock(callback=mock_callback)

    main()

    # Verify that logging setup was called
    mock_logger_setup.assert_called_once()

    # Verify that the command's callback was executed
    mock_callback.assert_called_once_with(mock_parser.parse_args.return_value)
    mock_logger.debug.assert_called_with(
        "Executing command callback: %s",
        mock_callback
    )


def test_main_without_command(mock_parser, mock_logger_setup, mock_logger):
    """Test main with no command provided (no callback)"""
    # Mocking parsed arguments without a callback
    mock_parser.parse_args.return_value = mock.Mock(callback=None)

    main()

    # Verify that logging setup was called
    mock_logger_setup.assert_called_once()

    # Verify that print_help was called when no callback is provided
    mock_parser.print_help.assert_called_once()
    mock_logger.debug.assert_called_with("No callback found, printing help")
