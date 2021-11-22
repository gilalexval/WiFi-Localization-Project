from win32wifi.Win32Wifi import getWirelessInterfaces
from win32wifi.Win32Wifi import getWirelessNetworkBssList
from win32wifi.Win32NativeWifiApi import WlanScan
from win32wifi.Win32NativeWifiApi import WlanOpenHandle
from win32wifi.Win32NativeWifiApi import WlanCloseHandle
from GetAPInfo import GetAPInfo
from GetDistance import distanceFromRSSI
from scipy.optimize import minimize
from trilateration import mse

import datetime

if __name__ == "__main__":
    ifaces = getWirelessInterfaces()
    distances = []
    locations = []
    initial_location = (1, 1)
    # print(ifaces)
    # print(len(ifaces))
    for iface in ifaces:
        print(iface)
        guid = iface.guid
        handle = WlanOpenHandle()
        WlanScan(handle, guid)
        WlanCloseHandle(handle)
        bsss = getWirelessNetworkBssList(iface)
        print()
        with open("WiFi_Log.log", 'a') as log:
            log.write("\n" + "-" * 25 +
                      datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "-" * 25)
        for bss in bsss:
            with open("WiFi_Log.log", 'a') as log:
                log.write("\nBSSID: " + bss.bssid + " SSID: " +
                          bss.ssid.decode("utf-8") + " RSSI: " + str(bss.rssi))
            print("BSSID: " + bss.bssid)
            print("SSID: " + bss.ssid.decode("utf-8"))
            print("RSSI: " + str(bss.rssi))
            APLocation, APMValue = GetAPInfo(bss.bssid)
            # print(APLocation)
            # print(APMValue)
            distance = distanceFromRSSI(bss.rssi, APMValue)
            print("Distance: " + str(distance))
            if distance is not None and APLocation is not None:
                distances.append(distance)
                locations.append(APLocation)
            print("-" * 20)
        print()
        print(distances)
        print(locations)
        result = minimize(
            mse,                            # The error function
            initial_location,               # The initial guess
            args=(locations, distances),    # Additional parameters for mse
            method='L-BFGS-B',              # The optimisation algorithm
            options={
                'ftol': 1e-5,               # Tolerance
                'maxiter': 1e+7             # Maximum iterations
            })
        print(result.x)

# Trilateration
# d1^2 = (x-x1)^2 + (y-y1)^2
# d2^2 = (x-x2)^2 + (y-y2)^2
# d3^2 = (x-x3)^2 + (y-y3)^2
#
# di es la distancia del APi al equipo (calculado con RSSI)
# xi es la coordenada en x del APi (Dato conocido)
# yi es la coordenada en y del APi (Dato conocido)
# x es la coordenada del dispositivo que se quiere encontrar
# y es la coordenada del dispositivo que se quiere encontrar
# Cuando (x,y) satisface las 3 ecuaciones, se tiene la ubicación exacta del punto

# Necesito una estructura:
# [(
#   BSSID: String (AB:AB:AB:AB:AB:AB)
#   Location: (x , y)
#   MValue : Int (-0 - -100)
# )]
