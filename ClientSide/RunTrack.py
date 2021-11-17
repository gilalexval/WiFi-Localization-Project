#************************************************#
# App: RunTrack (Client)                         #
# Version: 0.1.0                                 #
# Autor: Gilberto Valenzuela                     #
# Description: The app scan for networks,        #
# captures BSSID, SSID and RSSI and send it to   #
# a server for processing.                       #
#************************************************#
from win32wifi.Win32Wifi import getWirelessInterfaces
from win32wifi.Win32Wifi import getWirelessNetworkBssList
from win32wifi.Win32NativeWifiApi import WlanScan
from win32wifi.Win32NativeWifiApi import WlanOpenHandle
from win32wifi.Win32NativeWifiApi import WlanCloseHandle
from AppClient import start_comm

import datetime
import time
import json
import sys

try:
    with open('config.json', 'r') as c:
        config = json.load(c)

    print(config)
except FileNotFoundError:
    print("config.json not found")
    sys.exit()

if __name__ == "__main__":
    ifaces = getWirelessInterfaces()  # Get Network Interfaces/adapters
    data = ""  # Initialize empty string to store data
    for iface in ifaces:  # Iterate all network adapters
        # print(iface)
        handle = WlanOpenHandle()  # Assign handle
        # Scan for Networks on the specified interface
        # for i in range(2):
        # WlanScan returns inmediately. But the scan is done by the WiFi driver in the background
        WlanScan(handle, iface.guid)
        # Windows Systems are suppoused to finish a scan in under 4s. I set 5s just to be sure.
        time.sleep(5)
        WlanCloseHandle(handle)  # Close Handle
        # Get all information captures of all networks scanned
        # Returns the saved available list of networks. It performs an extra WlanScan but we don´t get the information from that scan but from the previous one. If this only return one element. The previous Wlan Scan didn´t finish.
        bsss = getWirelessNetworkBssList(iface)
        data += "\n" + "-" * 25 + \
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + \
            "-" * 25 + "\n"  # Write a time stamp
        for bss in bsss:  # Iterate all networks
            data += "BSSID: " + bss.bssid + " SSID: " + \
                bss.ssid.decode(
                    "utf-8") + " RSSI: " + str(bss.rssi) + "\n"  # Write BSSID, SSID and RSSI of the networks
        with open("WiFi_Log.log", 'a') as log:  # Append logfile
            # Write Logfile with the captured data of the networks
            log.write(data)
        print(data)  # Print data to console
        start_comm(config["Host"], config["Port"],
                   '', data)  # Send data to server
