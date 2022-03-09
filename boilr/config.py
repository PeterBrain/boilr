import os, sys
import json
import yaml
import logging

#with open("config.json", "r") as json_file:
#    user_config = json.safe_load(json_file)

with open("../config.yaml", "r") as yaml_file:
    user_config = yaml.safe_load(yaml_file)
    #logger.debug("Parsed configuration file: {0}".format(yaml_file.name))

app_config = user_config["boilr"] or []
rpi_config = user_config["rpi"] or []
rest_config = user_config["endpoint"] or []

#for item in user_config:
#  print(item)

prog_name = "boilr" # program name

rpi_channel_relay_out = rpi_config['rpi_channel_relay_out'] or 17 # board number 11
rpi_channel_relay_in = rpi_config['rpi_channel_relay_in'] or 27 # board number 13

interval = app_config['interval'] or 10 # check fronius api every x seconds
start_timeout = app_config['start_timeout'] or 2 # min time between switching off and on again in minutes

moving_median_list_size = app_config['moving_median_list_size'] or 5 # size of the array for past request values
charge_threshold = app_config['charge_threshold'] or 85 # min battery state of charge in %
ppv_tolerance = app_config['ppv_tolerance'] or 100 # tolerance pv production in W

heater_power = app_config['heater_power'] or 2600 # power of the heating element in W (power availability) (2550W in datasheet)

active_date_range = app_config['active_date_range'] or ["01-01", "31-12"] # may - oct (day-month) ([start, end])
active_time_range = app_config['active_time_range'] or ["00:00", "23:59"] # after charging the battery; before discharging the battery (hour:minute) 10:00 - 17:00 ([start, end])

request_timeout = rest_config['request_timeout'] or 5 # timeout for requests in seconds
scheme = rest_config['scheme'] or "http://"
ip = rest_config['ip'] or "10.0.10.90" # ip address of the inverter
api = rest_config['api'] or "/solar_api/v1" # api version (inverter specific; check with this URI: http://<ip-address>/solar_api/GetAPIVersion.cgi)
powerflow = rest_config['powerflow'] or "/GetPowerFlowRealtimeData.fcgi" # resource

working_directory = "/var/log/" + prog_name #"/var/lib/boilr/"
logpath = os.path.join(working_directory, prog_name + ".log") #"/var/log/boilr/boilr.log"
pidpath = os.path.join(working_directory, prog_name + ".pid") #"/var/run/boilr.pid"
chroot_dir = None #working_directory

#user_config.close()

#logger.debug("Finished applying configuration")
