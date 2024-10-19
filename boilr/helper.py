"""Helper module"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def date_check(active_date_range):
    """
    Function check if current date is within the active date range

    Parameters
    ----------
    active_date_range : list(str)
        Date range in which check should be positive

    Returns
    -------
    tuple
        status of check, message

    Raises
    ------
    ToDo
    Exception
        General exception
    """
    logger.debug("Checking date")

    current_date = datetime.now()
    current_month = current_date.strftime("%d-%m")
    current_month_and_day = datetime.strptime(current_month, "%d-%m")

    try:
        active_date_start, active_date_end = \
            [datetime.strptime(_, "%d-%m") for _ in active_date_range]
    except Exception as e:
        msg = f"Active date range conversion failed: {e}"
        logger.error(msg)
        return(False, msg)
    else:
        if active_date_start <= current_month_and_day <= active_date_end:
            msg = "Date within active range"
            logger.debug(msg)
            return(True, msg)
        else:
            msg = f"Date is not in active range. Active date range is set to: \
                {active_date_start.strftime('%d %B')} - {active_date_end.strftime('%d %B')}"
            logger.debug(msg)
            return(False, msg)


def time_check(active_time_range):
    """
    Check if current time is within the active time range

    Parameters
    ----------
    active_time_range : list(str)
        Time range in which check should be positive

    Returns
    -------
    tuple
        status of check, message

    Raises
    ------
    ToDo
    Exception
        General exception
    """
    logger.debug("Checking time")

    current_time = datetime.now().time()
    current_time_str = current_time.strftime("%H:%M")
    current_hour_and_minute = datetime.strptime(current_time_str, "%H:%M")

    try:
        active_time_start, active_time_end = \
            [datetime.strptime(_, "%H:%M") for _ in active_time_range]
    except Exception as e:
        msg = f"Active time range conversion failed: {e}"
        logger.error(msg)
        return(False, msg)
    else:
        if active_time_start <= current_hour_and_minute <= active_time_end:
            msg = "Time within active range"
            logger.debug(msg)
            return(True, msg)
        else:
            msg = f"Time is not in active range. Active time range is set to: \
                {active_time_start.strftime('%H:%M')} - {active_time_end.strftime('%H:%M')}"
            logger.debug(msg)
            return(False, msg)
