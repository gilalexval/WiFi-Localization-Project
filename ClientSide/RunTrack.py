#************************************************#
# App: RunTrack (Client)                         #
# Version: 1.2.2                                 #
# Autor: Gilberto Valenzuela                     #
# Description: The app scan for networks,        #
# captures BSSID, SSID and RSSI and send it to   #
# a server for processing.                       #
#************************************************#

#La aplicación depende de la libreria win32wifi para
#acceder a la API de Windows que gestiona la tarjeta de red
#https://github.com/kedos/win32wifi
from win32wifi.Win32Wifi import getWirelessInterfaces
from win32wifi.Win32Wifi import getWirelessNetworkBssList
from win32wifi.Win32NativeWifiApi import WlanScan
from win32wifi.Win32NativeWifiApi import WlanOpenHandle
from win32wifi.Win32NativeWifiApi import WlanCloseHandle

#Se utiliza el método start_comm de la aplicación AppClient
#para enviar los datos a través de la red.
#El codigo de AppClient es una copia modificada del ejemplo de Application Client en:
#https://realpython.com/python-sockets/
from AppClient import start_comm

import datetime
import time
import json
import re
import socket
import sys

try:
    #Abre el fichero config.json y carga el contenido en la variable config
    with open('config.json', 'r') as c:
        config = json.load(c) 
except FileNotFoundError:
    #Si no encuentra el archivo config en la misma carpeta donde esta la aplicación, crea un default
    print("config.json not found. Creating one...")

    #Host, es la IP del servidor al que debe enviar los datos
    #Port, es el puerto por el que envia los datos, debe estar desbloqueado
    #SidisConf, es la ruta al AppSettings de SIDIS, de donde lee el TestUnitId del equipo
    config = {"Host": '10.203.104.209', "Port": 55555,
              "SidisConf": "C:\\SIDIS\\Runtime\\Binaries\\AppSettings.config"}
    
    #crea el archivo config.json
    with open('config.json', 'w') as c:
        json.dump(config, c, indent=4)
try:
    #pattern, almacena una expresión regular que almacena el valor asignado al parametro TestUnitId
    pattern = r'(?m)^\s*<add key="TestUnitId"\s*value="(.*)"\s*/>'
    
    #Abre el fichero AppSettings.config de la ruta almacenada en el diccionario config con la llave SidisConf
    with open(config["SidisConf"], 'r') as c:
        #Busca en el contenido del fichero si existe una coincidencia con la expresión regular almacenada en pattern
        result = re.search(pattern, c.read())
        #Si existe alguna coincidencia
        if result is not None:
            #almacena el valor del TestUnitId en la variable sender
            sender = result.group(1)

        #Si no encuentra una coincidencia asigna la dirección IP del equipo a sender. Solo funciona con DNS.    
        else:
            hostname = socket.gethostname()
            sender = socket.gethostbyname(hostname)

except FileNotFoundError:
    #Si no encuentra el fichero en la ruta asigna la dirección IP del equipo a sender. Solo funciona con DNS.
    hostname = socket.gethostname()
    sender = socket.gethostbyname(hostname)

if __name__ == "__main__":
    ifaces = getWirelessInterfaces()  # Get Network Interfaces/adapters
    data = ""  # Initialize empty string to store data
    for iface in ifaces:  # Iterate all network adapters
        handle = WlanOpenHandle()  # Assign handle
        # Scan for Networks on the specified interface
        # WlanScan returns inmediately. But the scan is done by the WiFi driver in the background
        try:
            WlanScan(handle, iface.guid)
        except:
            with open("Err.log", "a") as errlog:
                errlog.write(datetime.datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S') + " WlanScan(handle, iface.guid) Failed" + "\n")
            WlanCloseHandle(handle)  # Close Handle
            sys.exit()
        # Windows Systems are suppoused to finish a scan in under 4s. I set 5s just to be sure.
        time.sleep(5)
        try:
            WlanCloseHandle(handle)  # Close Handle
        except:
            with open("Err.log", "a") as errlog:
                errlog.write(datetime.datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S') + " WlanCloseHandle(handle) Failed" + "\n")
                
        # Get all information captures of all networks scanned
        # Returns the saved available list of networks. It performs 
        # an extra WlanScan but we don´t get the information from that scan but from the previous one. 
        # If this only return one element. The previous Wlan Scan didn´t finish.
        try:
            bsss = getWirelessNetworkBssList(iface)
        except:
            with open("Err.log", "a") as errlog:
                errlog.write(datetime.datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S') + " getWirelessNetworkBssList(iface) Failed" + "\n")
            sys.exit()
        data += "\n" + "-" * 25 + \
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + \
            "-" * 25 + "\n"  # Write a time stamp
        for bss in bsss:  # Iterate all networks
            # Write BSSID, SSID and RSSI of the networks
            data += "BSSID: " + bss.bssid + " SSID: " + \
                bss.ssid.decode(
                    "utf-8") + " RSSI: " + str(bss.rssi) + "\n"
        # Overwrite logfile
        with open("WiFi_Log.log", 'w') as log:  
            # Write Logfile with the captured data of the networks
            log.write(data)

        # Send data to server
      
        try:
            start_comm(config["Host"], config["Port"],
                   sender, data)
        except:
            with open("Err.log", "a") as errlog:
                errlog.write(datetime.datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S') + " start_comm: Unable to send data" + "\n")
            sys.exit()