import re
import math
from trilateration import GetPosition


def GetBSSIDs():
    radioMAC = []
    APData = {"RadioMAC": [], "RSSI": [], "Distance": [], "Location": []}
    logPattern = r"(?m)^-{25}(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})-{25}\s((?:BSSID:\s.*\sSSID:\s.*\sRSSI:\s.*\n)*(?![^.]))"
    with open('ClientMsgs.log', 'r') as log:
        logData = re.search(logPattern, log.read())
    data = logData.group(3)
    BSSIDPattern = r"BSSID:\s*([\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2})\s*SSID:\s*(.*)\s*RSSI:\s*(-\d{1,3})?"
    BSSIDData = re.findall(BSSIDPattern, data)
    for item in BSSIDData:
        radMAC = item[0][:16].lower() + "0"
        if radMAC not in radioMAC:
            radioMAC.append(radMAC)
            APInfo = GetAPInfo(radMAC)
            if APInfo is not None:
                APData["RadioMAC"].append(APInfo.group(6))
                rssi = int(item[2])
                APData["RSSI"].append(rssi)
                APData["Location"].append(
                    (float(APInfo.group(3)), float(APInfo.group(4))))
                APData["Distance"].append(distanceFromRSSI(
                    rssi, int(APInfo.group(7))))
    bestSignal = -100
    for signal in APData["RSSI"]:
        if signal > bestSignal:
            bestSignal = signal
            listIndex = APData["RSSI"].index(bestSignal)
    closerAP = APData["Location"][listIndex]
    position = GetPosition(closerAP, APData["Location"], APData["Distance"])
    return position


def GetAPInfo(radMAC):
    pattern = r'(?m)^\s*"(.*)":\s*{[^}]*"Building":[^"]*"(.*)",[^}]*"X":[^"]*"(.*)m",[^}]*"Y":[^"]*"(.*)m",[^}]*"Z":[^"]*"(.*)m",[^}]*"RadioMAC":[^"]*"(' + \
        radMAC + ')",[^}]*"TxPower":[^"]*"(.*)",?[^}]*}'
    APsDB = "../APListMRT.json"

    with open(APsDB, 'r') as APs:
        result = re.search(pattern, APs.read())
        return result


def distanceFromRSSI(RSSI, powerLvl):
    # Calculate Distance from AP with the Formula
    #   Distance/(RefDist = 1m) = 10^((MeasuredPower@1m - RSSI)/(10*n))
    # Donde:
    # MeasuredPower -> RSSI a 1 m del AP (RefDist)
    # RSSI -> Leido por el dispositivo
    # n -> un factor entre 2 y 4 dependiente del nivel de interferencias que puede haber
    # measuredpower = -35 -> se puede reemplazar por TxPower en dBm

    # From Cisco Data Sheet. TxPower is the escale of the power used to radiate the signal. This is not mesured power at 1 m.
    if powerLvl == 1:
        TxPower = 23
    elif powerLvl == 2:
        TxPower = 20
    elif powerLvl == 3:
        TxPower = 17
    elif powerLvl == 4:
        TxPower = 14
    elif powerLvl == 5:
        TxPower = 11
    elif powerLvl == 6:
        TxPower = 8
    elif powerLvl == 7:
        TxPower = 5
    elif powerLvl == 8:
        TxPower = 2
    else:
        TxPower = None
    n = 2
    if TxPower is not None:
        # Since we don't have the mesured power at 1 m the original formula gives a very large distance, because the TxPower used here is the really the power used to feed the antena. Virtually this TxPower it should be the power we get at 0m, but it is imposible to get or mesure, thats why the reference distance is usually 1m. For this, the reference distance should be near to 0 (0.001 works in this case) and it should multiply the rest of the expresion.See the path loss model to get deeper in the math behind it.
        distance = (math.pow(10, ((TxPower - RSSI)/(10 * n)))) * 0.001
        return distance
    return None

    # fieldpattern = r'[^"]*"Campus":[^"]*"(.*)"'

    # for AP in result:
    # if AP[0] == APName:
    # print("BSSID: " + AP[0])
    # print("SSID: " + AP[1])
    # print("MValue: " + AP[2])
    # print("Hall: " + AP[3])
    # print("Column: " + AP[4])
    # print("x: " + AP[5])
    # print("y: " + AP[6])
    # coordinates = [int(AP[5])]
    # coordinates.append(int(AP[6]))
    # return tuple(coordinates), int(AP[2])
    # return None, None


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
