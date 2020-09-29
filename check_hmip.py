#!/opt/check_hmip/venv/bin/python3

import homematicip
from homematicip.home import Home
from homematicip.device import *
import datetime
import sys

# def write_plugableswitchmeasuring(room,device):
#     print(room, " ", device.label, " ", device.lastStatusUpdate, " ", device.currentPowerConsumption, " ", device.energyCounter)
#
# def write_heatingthermostat(room,device):
#     print(room, " ", device.label, " ", device.lastStatusUpdate)
#
# def write_wallmountedthermostatpro(room,device):
#     print(room, " ", device.label, " ", device.lastStatusUpdate, " ", device.actualTemperature, " ", device.setPointTemperature, " ", device.humidity)

if __name__ == "__main__":

    sys.stdout.write("<<<local>>>\n")
    try:
        config = homematicip.find_and_load_config_file()
        if config is None:
            raise Exception("Config cannot be loaded")

        home = Home()
        home.set_auth_token(config.auth_token)
        home.init(config.access_point)

        if home.get_current_state() is False:
            raise Exception("Cannot get current state")

        for g in home.groups:
            if g.groupType=="META":
                for device in g.devices:
                    state = 'P'
                    statetext='OK'

                    # room name / device names
                    service = f"{g.label.replace(' ', '_')}/{device.label.replace(' ', '_')}"

                    # last status update from device in seconds
                    lastseen = (datetime.datetime.now() - device.lastStatusUpdate).total_seconds()
                    WARNLASTSEEN = 5000
                    CRITLASTSEEN = 4*3600

                    # RSSI seen from the AP
                    rssiDeviceValue = device.rssiDeviceValue
                    WARNRSSI = -80
                    CRITRSSI = -90

                    # battery
                    lowbat = device.lowBat
                    if lowbat:
                        state = '1'
                        statetext = 'LOWBAT'

                    # unreachable status
                    unreach = device.unreach
                    if lowbat:
                        state = '2'
                        statetext = 'UNREACH'

                    # has uninstalled updates
                    updateState = device.updateState
                    if updateState != DeviceUpdateState.UP_TO_DATE:
                        state = '1'
                        statetext = updateState

                    # has config pending
                    configPending = device.configPending
                    if configPending:
                        state = '1'
                        statetext = 'CONFIGPENDING'

                    # check plugin further messages
                    details = f"{device.deviceType} ({device.firmwareVersion})"

                    # device specific messages
                    if isinstance(device, ShutterContact):
                        details += f" Window: {device.windowState}"
                    elif isinstance(device, PlugableSwitch):
                        details += f" State: {'ON' if device.on else 'OFF'}," \
                                   f" Userdesired: {device.userDesiredProfileMode}"
                    else:
                        details += f" Unknown device seen, please update the check script with its details."

                    sys.stdout.write(f"{state} {service} "
                                     f"lastseen={lastseen};{WARNLASTSEEN};{CRITLASTSEEN},"
                                     f"|RSSI={rssiDeviceValue};{WARNRSSI}:0;{CRITRSSI}:0;-100;0"
                                     f" {statetext} - {details}\n" )
    except Exception as e:
        sys.stderr.write(f"HMIP-REST-API ERROR - {e}\n")
        exit(-1)
