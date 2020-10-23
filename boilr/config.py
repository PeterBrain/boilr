import os, sys

prog_name = "boilr" # program name

interval = 10 # check fronius api every x seconds
rpi_channel_relay_out = 17 # board number 11
rpi_channel_relay_in = 27 # board number 13

moving_median_list_size = 5 # size of the array for past request values
charge_threshold = 85 # min battery state of charge in %
ppv_tolerance = 100 # tolerance pv production in W
pgrid_tolerance = 500 # tolerance power from grid in W
pakku_tolerance = 500 # tolerance power from akku in W

heater_power = 2600 # power of the heating element in W (power availability)

active_date_range = ["01-05", "31-10"] # may - oct (day-month)
active_time_range = ["10:30", "16:30"] # after charging the battery; before discharging the battery (hour:minute) 11:00 - 16:30

request_timeout = 5 # timeout for requests in seconds
scheme = "http://"
ip = "10.0.10.90" # ip address of the inverter
api = "/solar_api/v1" # api version (inverter specific; check with this URI: http://<ip-address>/solar_api/GetAPIVersion.cgi)
powerflow = "/GetPowerFlowRealtimeData.fcgi" # resource

working_directory = "/var/log/" + prog_name #"/var/lib/boilr/"
logpath = os.path.join(working_directory, prog_name + ".log") #"/var/log/boilr/boilr.log"
pidpath = os.path.join(working_directory, prog_name + ".pid") #"/var/run/boilr.pid"
chroot_dir = None #working_directory
