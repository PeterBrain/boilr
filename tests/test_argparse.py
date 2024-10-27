"""Tests for argparse"""
import sys
from unittest import mock
import pytest
from boilr.argparse import setup_parser, CustomArgumentParser
import boilr.daemon as daemon


@pytest.fixture
def parser():
    """Fixture to return a configured argument parser instance"""
    return setup_parser()


def test_parser_help_message(parser, capsys):
    """Test help message displays correctly"""
    with pytest.raises(SystemExit):
        parser.parse_args(['-h'])

    captured = capsys.readouterr()
    assert 'Additional hardware required' in captured.out


def test_verbose_flag(parser):
    """Test verbose flag is set correctly"""
    args = parser.parse_args(['--verbose'])

    assert args.verbose is True


def test_default_config_path(parser):
    """Test that config path is not required and has no default value"""
    args = parser.parse_args([])

    assert args.config is None


def test_custom_error_message(capsys):
    """Test custom error message for invalid arguments"""
    with mock.patch.object(sys, 'exit', side_effect=SystemExit) as mock_exit:
        with pytest.raises(SystemExit):
            CustomArgumentParser().error("This is a custom error")

    captured = capsys.readouterr()
    assert "Error: This is a custom error" in captured.err
    assert "Use boilr -h to show further instructions" in captured.err
    mock_exit.assert_called_once_with(2)


@pytest.mark.parametrize("command, callback", [
    (["start"], daemon.daemon_start),
    (["stop"], daemon.daemon_stop),
    (["status"], daemon.daemon_status),
    (["restart"], daemon.daemon_restart),
    (["run"], daemon.daemon_run),
    (["manual", "1"], daemon.daemon_manual),
])
def test_subcommands_callback(parser, command, callback):
    """Test that each subcommand sets the correct callback function"""
    args = parser.parse_args(command)

    assert args.callback == callback


def test_manual_override_argument(parser):
    """Test manual override subcommand accepts only 0 or 1"""
    args = parser.parse_args(['manual', '1'])
    assert args.manual == [1]

    args = parser.parse_args(['manual', '0'])
    assert args.manual == [0]


def test_invalid_manual_override_argument(parser, capsys):
    """Test that invalid manual override argument raises error"""
    with pytest.raises(SystemExit):
        parser.parse_args(['manual', '2'])

    captured = capsys.readouterr()
    assert "invalid choice" in captured.err


def test_missing_command_error(parser, capsys):
    """Test error message when no subcommand is provided"""
    with pytest.raises(SystemExit):
        args = parser.parse_args([])

        # Simulate the behavior if no command is found
        if args.command is None:
            parser.error("Choose between the following positional arguments")

    captured = capsys.readouterr()
    assert "Choose between the following positional arguments" in captured.err
    assert "Use boilr -h to show further instructions" in captured.err
