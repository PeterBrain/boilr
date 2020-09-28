from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def date_checker(active_date_range):
    logger.debug("checking date")

    current_date = datetime.now()
    current_month = current_date.strftime("%d-%m")
    current_month_and_day = datetime.strptime(current_month, "%d-%m")

    try:
        active_date_start, active_date_end = [datetime.strptime(_, "%d-%m") for _ in active_date_range]
    except:
        logger.error("Active date range coversion failed - asuming date is in range")
        active_date_start = active_date_end = current_date

    if active_date_start <= current_month_and_day <= active_date_end:
        logger.debug("Date within active range")
        return(True, "")
    else:
        logger.info("Date is not in active range")
        return(False, "Date is not in active range")


def time_checker(active_time_range):
    logger.debug("checking time")

    current_time = datetime.now().time()
    current_time_str = current_time.strftime("%H:%M")
    current_hour_and_minute = datetime.strptime(current_time_str, "%H:%M")

    try:
        active_time_start, active_time_end = [datetime.strptime(_, "%H:%M") for _ in active_time_range]
    except:
        logger.error("Active time range coversion failed - asuming time is in range")
        active_time_start = active_time_end = current_time

    if active_time_start <= current_hour_and_minute <= active_time_end:
        logger.debug("Time within active range")
        return(True, "")
    else:
        logger.info("Time is not in active range")
        return(False, "Time is not in active range")
