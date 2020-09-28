#!/opt/check_hmip/venv/bin/python3

import homematicip
from homematicip.home import Home
from homematicip.device import *
import datetime

def write_shutter(room,device):
    print(room, " ", device.label, " ", device.lastStatusUpdate, " ", device)

def write_shutter(room,device):
    print(room, " ", device.label, " ", device.lastStatusUpdate, " ", device.windowState)

def write_plugableswitchmeasuring(room,device):
    print(room, " ", device.label, " ", device.lastStatusUpdate, " ", device.currentPowerConsumption, " ", device.energyCounter)

def write_heatingthermostat(room,device):
    print(room, " ", device.label, " ", device.lastStatusUpdate)

def write_wallmountedthermostatpro(room,device):
    print(room, " ", device.label, " ", device.lastStatusUpdate, " ", device.actualTemperature, " ", device.setPointTemperature, " ", device.humidity)

def write_unknown(room,device):
    print("Unknown device in ", room, " ", type(d))

if __name__ == "__main__":

    print("<<<local>>>")
    try:
        config = homematicip.find_and_load_config_file()
        if config is None:
            raise Exception("Config cannot be loaded")

        home = Home()
        home.set_auth_token(config.auth_token)
        home.init(config.access_point)

        home.get_current_state()
        for g in home.groups:
            if g.groupType=="META":
                for device in g.devices:
                    state = 'P'
                    statetext='OK'

                    service = f"{g.label.replace(' ', '_')}/{device.label.replace(' ', '_')}"
                    lastseen = (datetime.datetime.now() - device.lastStatusUpdate).total_seconds()
                    rssiDeviceValue = device.rssiDeviceValue

                    # check battery
                    lowbat = device.lowBat
                    if lowbat:
                        state = '1'
                        statetext = 'LOWBAT'

                    unreach = device.unreach
                    if lowbat:
                        state = '2'
                        statetext = 'UNREACH'

                    updateState = device.updateState
                    if updateState != DeviceUpdateState.UP_TO_DATE:
                        state = '1'
                        statetext = updateState

                    configPending = device.configPending
                    if configPending:
                        state = '1'
                        statetext = 'CONFIGPENDING'

                    details = f"{device.deviceType} ({device.firmwareVersion})"

                    if isinstance(device, ShutterContact):
                        details += f": {device.windowState}"
                    elif isinstance(device, PlugableSwitch):
                        details += f"\\\\nState: {'ON' if device.on else 'OFF'}" \
                                   f"\\\\nUserDesiredProfileMode: {device.userDesiredProfileMode}"

                    print(f"{state} {service} "
                          f"lastseen={lastseen};3600;7200"
                          f"|RSSI={rssiDeviceValue};-80:0;-90:0;-100;0"
                          f" {statetext} - {details}" )
    except Exception as e:
        print(f"2 HMIP-REST-API ERROR - {e}")
        exit(-1)
