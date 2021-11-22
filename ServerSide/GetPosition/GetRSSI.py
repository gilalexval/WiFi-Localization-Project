from win32wifi.Win32Wifi import getWirelessInterfaces
from win32wifi.Win32Wifi import getWirelessNetworkBssList

if __name__ == "__main__":
    ifaces = getWirelessInterfaces()
    for iface in ifaces:
        print(iface)
        guid = iface.guid
        bsss = getWirelessNetworkBssList(iface)
        print()
        for bss in bsss:
            print(bss.bssid)
            print(bss.ssid)
            print(bss.rssi)
            print("-" * 20)
        print()