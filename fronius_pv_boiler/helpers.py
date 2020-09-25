from datetime import datetime

def date_checker(active_date_range):
    current_date = datetime.now() #datetime(datetime.now().year, datetime.now().month, datetime.now().day)
    current_month = current_date.strftime("%d-%m") # returns string
    current_month_and_day = datetime.strptime(current_month, "%d-%m")
    active_date_start, active_date_end = [datetime.strptime(_, "%d-%m") for _ in active_date_range]
    #active_start = datetime.datetime.strptime("02-05", "%d-%m")
    #active_end = datetime.datetime.strptime("31-10", "%d-%m")

    if active_date_start <= current_month_and_day <= active_date_end: #active_start.month <= current_date.month <= active_end.month
        return(True, "")
    else:
        return(False, "Date is not in active range")


def time_checker(active_time_range):
    current_time = datetime.now().time()
    current_time_str = current_time.strftime("%H:%M")
    current_hour_and_minute = datetime.strptime(current_time_str, "%H:%M")
    active_time_start, active_time_end = [datetime.strptime(_, "%H:%M") for _ in active_time_range]

    if active_time_start <= current_hour_and_minute <= active_time_end:
        return(True, "")
    else:
        return(False, "Time is not in active range")
