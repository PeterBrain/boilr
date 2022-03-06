import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def date_checker(active_date_range):
    logger.debug("Checking date")

    current_date = datetime.now()
    current_month = current_date.strftime("%d-%m")
    current_month_and_day = datetime.strptime(current_month, "%d-%m")

    try:
        active_date_start, active_date_end = [datetime.strptime(_, "%d-%m") for _ in active_date_range]
    except Exception as e:
        msg = "Active date range conversion failed"
        logger.error(msg)
        return(False, msg)
    else:
        if active_date_start <= current_month_and_day <= active_date_end:
            msg = "Date within active range"
            logger.debug(msg)
            return(True, msg)
        else:
            msg = "Date is not in active range"
            logger.debug(msg)
            return(False, msg)


def time_checker(active_time_range):
    logger.debug("Checking time")

    current_time = datetime.now().time()
    current_time_str = current_time.strftime("%H:%M")
    current_hour_and_minute = datetime.strptime(current_time_str, "%H:%M")

    try:
        active_time_start, active_time_end = [datetime.strptime(_, "%H:%M") for _ in active_time_range]
    except Exception as e:
        msg = "Active time range conversion failed"
        logger.error(msg)
        return(False, msg)
    else:
        if active_time_start <= current_hour_and_minute <= active_time_end:
            msg = "Time within active range"
            logger.debug(msg)
            return(True, msg)
        else:
            msg = "Time is not in active range"
            logger.debug(msg)
            return(False, msg)


# https://github.com/jaraco/jaraco.docker/blob/main/jaraco/docker.py
# https://stackoverflow.com/questions/20010199/how-to-determine-if-a-process-runs-inside-lxc-docker
# https://stackoverflow.com/questions/43878953/how-does-one-detect-if-one-is-running-within-a-docker-container-within-python
def text_in_file(text, filename):
    return any(text in line for line in open(filename))


def is_docker():
    """
    Is this current environment running in docker?
    >>> type(is_docker())
    <class 'bool'>
    """
    return os.path.exists('/.dockerenv') or text_in_file('docker', '/proc/self/cgroup')
