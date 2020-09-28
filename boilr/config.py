interval = 10 # check fronius api every x seconds
rpi_pin_relais = 17 # board number 11 (first non-special gpio)
charge_threshold = 20 # min battery state of charge in %
ppv_threshold = 100 # min pv production in W

active_date_range = ["01-05", "31-10"] # may - oct (day-month)
active_time_range = ["00:00", "23:59"] # after charging the battery; before discharging the battery (hour:minute) 11:00 - 16:30

request_timeout = 5 # timeout for requests in seconds
scheme = "http://"
ip = "10.0.10.90" # ip address of the inverter
api = "/solar_api/v1" # api version (inverter specific; check with this URI: http://<ip-address>/solar_api/GetAPIVersion.cgi)
powerflow = "/GetPowerFlowRealtimeData.fcgi" # resource

working_directory = "/var/log/boilr" #"/var/lib/boilr/"
logfile = working_directory + "/boilr.log"#"/var/log/boilr/boilr.log"
pid_lockfile = working_directory + "/boilr.pid" #"/var/run/boilr.pid"
chroot_dir = None #working_directory
