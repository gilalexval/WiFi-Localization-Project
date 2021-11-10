import re

pattern = r'{\s*"BSSID":\s*"(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})",\s*"SSID":\s*"(.*)",\s*"MValue":\s*"(-\d*)",\s*"Location":\s*{\s*"Hall":\s*"(\w*)",\s*"Column":\s*"(\w*)",\s*"Coordinates":\s*\[\s*"(\d*)",\s*"(\d*)"\s*\]\s*}\s*}'
APsDB = "./APs.json"

with open(APsDB, 'r') as APs:
    result = re.findall(pattern, APs.read())


def GetAPInfo(bssid):
    for AP in result:
        if AP[0] == bssid:
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
