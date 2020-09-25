from fronius_pv_boiler import helpers
import json
import requests
#import RPi.GPIO as GPIO

def run():
    rpi_gpio_relais = 17 # board number 11 (first non-special gpio)
    charge_threshhold = 0 # StateOfCharge_Relative

    active_date_range = ["01-05", "31-10"] # may - oct
    active_time_range = ["00:00", "23:30"] # after charging the battery; before discharging the battery 11:00 - 16:30

    url = "http://10.0.10.90"
    api = "/solar_api/v1"
    #inverter = "/GetInverterRealtimeData.cgi"
    #meter = "/GetMeterRealtimeData.cgi"
    #storage = "/GetStorageRealtimeData.cgi"
    powerflow = "/GetPowerFlowRealtimeData.fcgi"

    """payload_storage = {
        'Scope': 'System'
    }"""


    date_check = helpers.date_checker(active_date_range)
    if date_check[0]:

        time_check = helpers.time_checker(active_time_range)
        if time_check[0]:

            print("gathering information")

            #r = requests.get(url + "/solar_api/GetAPIVersion.cgi")
            #print(r.url)
            #print(r.status_code)
            #print(r.headers)
            #print(r.text)
            #print(r.json())
            #print(r.json()['BaseURL'])
            #json_api = r.json()
            #print(json_api['BaseURL'])

            #response_inverter = requests.get(url + api + inverter, params=payload_inverter)
            #print(response_inverter.json())

            ## storage
            """response_storage = requests.get(url + api + storage, params=payload_storage)
            storage_controller = response_storage.json()['Body']['Data']['0']['Controller']
            storage_soc = storage_controller['StateOfCharge_Relative'] # state of charge
            storage_idc = storage_controller['Current_DC'] # current"""

            ## power flow
            response_powerflow = requests.get(url + api + powerflow)
            powerflow_site = response_powerflow.json()['Body']['Data']['Site']
            powerflow_pgrid = powerflow_site['P_Grid'] or 0 # + from grid, - to grid, null no meter enabled
            powerflow_pakku = powerflow_site['P_Akku'] or 0 # - charge, + discharge, null not active
            powerflow_ppv = powerflow_site['P_PV'] or 0 # + production, null inverter not running
            powerflow_inverters = response_powerflow.json()['Body']['Data']['Inverters']['1']
            powerflow_soc = powerflow_inverters['SOC'] # state of charge

            #print(str(powerflow_pgrid) + ' ' + str(powerflow_pakku) + ' ' + str(powerflow_ppv))

            #GPIO.setmode(GPIO.BCM) # GPIO number (not board number)
            #GPIO.setup(rpi_gpio_relais, GPIO.OUT) # GPIO mode

            #if storage_soc >= charge_threshhold and storage_idc > -0.5 and meter_iac_p1 < 0.5 and meter_iac_p2 < 0.5 and meter_iac_p3 < 0.5:
            if powerflow_soc >= charge_threshhold and powerflow_pakku < 0 and powerflow_pgrid < 0:
                print("active")
                #output_relais(rpi_gpio_relais, GPIO.HIGH)
            else:
                print("inactive")
                #output_relais(rpi_gpio_relais, GPIO.LOW)
        else:
            print(time_check[1]) # not in time range
            #output_relais(rpi_gpio_relais, GPIO.LOW)
    else:
        print(date_check[1]) # not in date range
        #output_relais(rpi_gpio_relais, GPIO.LOW)
        #GPIO.output(rpi_gpio_relais, GPIO.LOW) # off


def output_relais(pin, state):
    #GPIO.output(pin, state)
    return True

if __name__ == '__main__':
    run()
