from fronius_pv_boiler import helpers
from fronius_pv_boiler import rpi_gpio
import json
import requests

rpi_gpio_relais = 17 # board number 11 (first non-special gpio)
charge_threshold = 20 # min battery state of charge in %
ppv_threshold = 100 # min pv production in W

active_date_range = ["01-05", "31-10"] # may - oct (%d-%m)
active_time_range = ["00:00", "23:30"] # after charging the battery; before discharging the battery (%H:%M) 11:00 - 16:30

url = "http://10.0.10.90"
api = "/solar_api/v1"
powerflow = "/GetPowerFlowRealtimeData.fcgi"


def run():
    date_check = helpers.date_checker(active_date_range)
    if date_check[0]:

        time_check = helpers.time_checker(active_time_range)
        if time_check[0]:

            print("gathering information\n")

            response_powerflow = requests.get(url + api + powerflow)

            powerflow_site = response_powerflow.json()['Body']['Data']['Site']
            powerflow_pgrid = powerflow_site['P_Grid'] or 0 # + from grid, - to grid, null no meter enabled
            powerflow_pakku = powerflow_site['P_Akku'] or 0 # + discharge, - charge, null not active
            powerflow_ppv = powerflow_site['P_PV'] or 0 # + production, null inverter not running

            powerflow_inverters = response_powerflow.json()['Body']['Data']['Inverters']['1']
            powerflow_soc = powerflow_inverters['SOC'] # state of charge

            rpi_gpio.gpio_relais(rpi_gpio_relais)

            if powerflow_soc >= charge_threshold and powerflow_pakku < 0 and powerflow_pgrid < 0 and powerflow_ppv > ppv_threshold:
                # soc over threshold & storage in charging mode & supply into grid & pv production over threshold
                print("Contactor: closed\nStatus: active")
                rpi_gpio.output_relais(rpi_gpio_relais, 1)
            else:
                print("Contactor: open\nStatus: inactive")
                rpi_gpio.output_relais(rpi_gpio_relais, 0)

        else:
            print(time_check[1]) # not in time range
            rpi_gpio.cleanup()
    else:
        print(date_check[1]) # not in date range
        rpi_gpio.cleanup()


if __name__ == '__main__':
    run()
