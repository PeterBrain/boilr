interval = 10 # check fronius api every x seconds
rpi_pin_relais = 17 # board number 11 (first non-special gpio)
charge_threshold = 20 # min battery state of charge in %
ppv_threshold = 100 # min pv production in W

active_date_range = ["01-05", "31-10"] # may - oct (%d-%m)
active_time_range = ["00:00", "23:59"] # after charging the battery; before discharging the battery (%H:%M) 11:00 - 16:30

url = "http://10.0.10.90"
api = "/solar_api/v1"
powerflow = "/GetPowerFlowRealtimeData.fcgi"

logfile = "/var/log/fronius_pv_boiler/boilr.log"
pid_lockfile = "/var/run/fronius_pv_boiler.pid"
working_directory = "/var/lib/fronius_pv_boiler"
