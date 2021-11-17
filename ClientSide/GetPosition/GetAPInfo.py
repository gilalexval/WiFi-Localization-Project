import re


def GetBSSIDs():
    logPattern = r"(?m)^-{25}(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})-{25}\s((?:BSSID:\s.*\sSSID:\s.*\sRSSI:\s.*\n)*(?![^.]))"
    with open('ClientMsgs.log', 'r') as log:
        logData = re.search(logPattern, log.read())
    data = logData.group(3)
    BSSIDPattern = r"BSSID:\s*([\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2})\s*SSID:\s*(.*)\s*RSSI:\s*(-\d{1,3})?"
    BSSIDData = re.findall(BSSIDPattern, data)
    for item in BSSIDData:
        bssid = item[0]
        ssid = item[1]
        rssi = item[2]
        # Call to function to get AP Info based on BSSID
        print(bssid)
        print(len(bssid))
        print(ssid)
        print(rssi)


def GetAPInfo(APName):
    pattern = r'^[^"]*"' + APName + '":[^{]*{([^}]*)}'
    APsDB = "./APListRMT.json"

    with open(APsDB, 'r') as APs:
        result = re.search(pattern, APs.read())

    fieldpattern = r'[^"]*"Campus":[^"]*"(.*)"'

    for AP in result:
        if AP[0] == APName:
            #print("BSSID: " + AP[0])
            #print("SSID: " + AP[1])
            #print("MValue: " + AP[2])
            #print("Hall: " + AP[3])
            #print("Column: " + AP[4])
            #print("x: " + AP[5])
            #print("y: " + AP[6])
            coordinates = [int(AP[5])]
            coordinates.append(int(AP[6]))
            return tuple(coordinates), int(AP[2])
    return None, None


# patron para buscar en la info de un AP especifico en json y capturarla
# '^[^"]*"MRTPT0887AP":[^{]*{([^}]*)}'

# Patron para buscar dentro de lo capturado anteriormente el valor de algún parametro especifico
# '[^"]*"Campus":[^"]*"(.*)"'

# patron para encontrar el último log enviado al servidor
# pattern = r"(?m)^-{25}(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})-{25}\s((?:BSSID:\s.*\sSSID:\s.*\sRSSI:\s.*\n)*(?![^.]))"
# match = re.search(pattern, text)

# patron para capturar los datos de los AP detectados por el ciente
# newp = r"BSSID:\s*([\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2})\s*SSID:\s*(.*)\s*RSSI:\s*(-\d{1,3})?"
# newm = re.findall(newp, data)
