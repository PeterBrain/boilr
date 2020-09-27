interval = 10 # check fronius api every x seconds
rpi_pin_relais = 17 # board number 11 (first non-special gpio)
charge_threshold = 20 # min battery state of charge in %
ppv_threshold = 100 # min pv production in W

active_date_range = ["01-05", "31-10"] # may - oct (day-month)
active_time_range = ["00:00", "23:59"] # after charging the battery; before discharging the battery (hour:minute) 11:00 - 16:30

url = "http://10.0.10.90"
api = "/solar_api/v1"
powerflow = "/GetPowerFlowRealtimeData.fcgi"

working_directory = "/var/log/boilr" #"/var/lib/boilr/"
logfile = working_directory + "/boilr.log"#"/var/log/boilr/boilr.log"
pid_lockfile = working_directory + "/boilr.pid" #"/var/run/boilr.pid"
chroot_dir = None #working_directory
