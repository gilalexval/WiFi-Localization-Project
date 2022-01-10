import re
import math
import numpy as np
from scipy.optimize import minimize
import math
import os
import json


def GetBSSIDs(logFilePath):  # Recibe la ruta del log con los datos de los APs escaneados
    # Extrae de la ruta el nombre del cliente que hizo el escaneo
    clientName, ext = os.path.splitext(os.path.basename(logFilePath))
    radioMAC = []  # Inicializa lista vacia para contener las MAC de los AP escaneados y evitar repeticiones
    APData = {"Name": [], "Hall": [], "RadioMAC": [],
              "RSSI": [], "Distance": [], "Coordinates": []}  # Inicializa diccionario de listas que contendran de manera ordenada los datos de cada AP encontrado
    # Guarda el patron para que la busqueda con expresiones regulares regrese solo el último escaneo contenido en el log. Ignora los escaneos anteriores.
    logPattern = r"(?m)^-{25}(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})-{25}\s((?:BSSID:\s.*\sSSID:\s.*\sRSSI:\s.*\n)*(?![^.]))"
    with open(logFilePath, 'r') as log:  # Abre archivo de log como lectura
        # Guarda la información del último escaneo contenido en el log
        logData = re.search(logPattern, log.read())
    # Guarda solo la información con todos los BSSID, SSID y RSSI del último escaneo
    data = logData.group(3)
    # Patron para que la busqueda regrese todos los BSSIDs del último escaneo
    BSSIDPattern = r"BSSID:\s*([\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2}:[\da-fA-F]{2})\s*SSID:\s*(.*)\s*RSSI:\s*(-\d{1,3})?"
    # Guarda todos los BSSID encontrados en data
    BSSIDData = re.findall(BSSIDPattern, data)
    for item in BSSIDData:  # Itera sobre cada resultado de que contiene BSSID, SSID y RSSI
        # Transformamos el BSSID encontrado en la MAC del radio que corresponde al AP que emitió la señal
        radMAC = item[0][:16].lower() + "0"
        if radMAC not in radioMAC:  # Verifica que sea la primera vez que consultamos los datos de esta MAC de este radio
            # Agrega la MAC a la lista para asegurar que solo consultaremos la información una vez
            radioMAC.append(radMAC)
            # Llamamos a la función que extrae la información de las MAC de las que se dispone de información
            APInfo = GetAPInfo(radMAC)
            if APInfo is not None:  # Verifica que haya información de regreso para la MAC consultada
                # APInfo.group(1) = AP Name
                # APInfo.group(2) = Hall
                # APInfo.group(3) = Coordinate x
                # APInfo.group(4) = Coordinate y
                # APInfo.group(5) = Coordiante z
                # APInfo.group(6) = Radio MAC
                # APInfo.group(7) = Tx Power Level
                # Guarda y convierte a entero el RSSI registrado para ese MAC
                rssi = int(item[2])
                # Lista en el diccionario el nombre del AP
                APData["Name"].append(APInfo.group(1))
                # Lista en el diccionario el taller del AP
                APData["Hall"].append(APInfo.group(2))
                # Lista en el diccionario la MAC del Radio del AP
                APData["RadioMAC"].append(APInfo.group(6))
                # Lista en el diccionario el RSSI leido del AP
                APData["RSSI"].append(rssi)
                APData["Coordinates"].append(
                    (float(APInfo.group(3)), float(APInfo.group(4))))  # Lista en el diccionario las coordenadas conocidas del AP
                APData["Distance"].append(distanceFromRSSI(
                    rssi, APInfo.group(7)))  # Utiliza el rssi y el Tx Power del AP para calcular la distancia en metros a la que estaba el cliente con respecto al AP al momento de la lectura
    if APData["RSSI"] != []:  # Verifica que la lista no este vacia. Si esta vacia, significa que no se tiene información del los APs capturados en el escaneo
        # Inicializa la variable con el valor de RSSI tan bajo que no es posible que algún cliente registre tal señal.
        bestSignal = -101
        # Itera los elementos de la lista del diccionario que contiene los RSSI capturados
        for signal in APData["RSSI"]:
            if signal > bestSignal:  # Compara el RSSI con el mejor RSSI leido hasta el momento
                # Si la señal que se esta comparando es mejor que la anteriormente guardada, esta la reemplaza
                bestSignal = signal
                # Obtenemos el indice de la lista el cual contiene la mejor señal registrada
                listIndex = APData["RSSI"].index(bestSignal)
        # this are the coordinates of the nearest AP based on which AP has the strongest signal
        # Con el indice de la lista extraemos las coordinadas del AP
        coordinatesClosestAP = APData["Coordinates"][listIndex]
        # Hall where the closest AP is located
        # Con el indice de la lista extraemos el Taller del AP
        hallClosestAP = APData["Hall"][listIndex]
        # Name of the closest AP
        # Con el indice de la lista extraemos el nombre del AP
        nameClosestAP = APData["Name"][listIndex]
        # position is the calculated position of the Client using trilateration. return
        position = GetPosition(coordinatesClosestAP,
                               APData["Coordinates"], APData["Distance"])
        # returns the Name, Hall and coordinates of the closest AP
        # return hallClosestAP, nameClosestAP, coordinatesClosestAP, clientName
        # return position  # returns the calculated position of the client
        try:
            # Abre el fichero positions.json, que contiene una relación de Talleres, APs y Clientes
            with open("positions.json", "r") as pos:
                # Carga el contenido formato json en una estructura de python
                positionsData = json.load(pos)
        except FileNotFoundError:  # Si no existe el fichero
            with open("positions.json", "a") as pos:  # Crea el fichero vacio positions.json
                positionsData = {}  # inicializa un diccionario como estructura base para le fichero json
        # Si el Taller del AP que se calculó es el mas cercano al cliente no está dentro de la estructura
        if hallClosestAP not in positionsData:
            # Crea un diccionario vacío dentro con el nombre de taller como Clave
            positionsData[hallClosestAP] = {}
        # Si el AP que se calculó es el mas cercano al cliente no está dentro de la estructura correspondiente al taller previamente especificado
        if nameClosestAP not in positionsData[hallClosestAP]:
            positionsData[hallClosestAP][nameClosestAP] = {
                "Coordinates": coordinatesClosestAP, "Clients": []}  # Crea un diccionario dentro del taller con el nombre del AP como clave y los parametros coordinates para guardar la ubbicación del AP y una lista clients que contendrá los clientes conectados a este AP
        # Si el cliente no se encuentra en la lista de clientes del AP en el taller especificado
        if clientName not in positionsData[hallClosestAP][nameClosestAP]["Clients"]:
            positionsData[hallClosestAP][nameClosestAP]["Clients"].append(
                clientName)  # Agregar el cliente a la lista de clientes del AP
        # Abre el fichero que contiene la relacion de Talleres, APs y Clientes en modo de lectura
        with open("positions.json", "w") as pos:
            # Sobre escribe la información actualizada
            json.dump(positionsData, pos, indent=4)
        return None  # Regresa None para indicar que el proceso ha terminado
    # Regresa este mensaje solo cuando no existe ningún registro de AP conocido
    return "No registered AP found for " + clientName


def GetAPInfo(radMAC):
    pattern = r'(?m)^\s*"(.*)":\s*{[^}]*"Building":[^"]*"(.*)",[^}]*"X":[^"]*"(.*)m",[^}]*"Y":[^"]*"(.*)m",[^}]*"Z":[^"]*"(.*)m",[^}]*"RadioMAC":[^"]*"(' + \
        radMAC + ')",[^}]*"TxPower":[^"]*"(.*)",?[^}]*}'
    APsDB = "./APListMRT.json"

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
    if powerLvl == '1':
        TxPower = 23
    elif powerLvl == '2':
        TxPower = 20
    elif powerLvl == '3':
        TxPower = 17
    elif powerLvl == '4':
        TxPower = 14
    elif powerLvl == '5':
        TxPower = 11
    elif powerLvl == '6':
        TxPower = 8
    elif powerLvl == '7':
        TxPower = 5
    elif powerLvl == '8':
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

def mse(x, Coordinates, distances):
    mse = 0.0
    for Coordinates, distance in zip(Coordinates, distances):
        distance_calculated = euclidean_distance(
            x[0], x[1], Coordinates[0], Coordinates[1])
        mse += math.pow(distance_calculated - distance, 2.0)
    return mse / len(distances)


def euclidean_distance(x1, y1, x2, y2):
    p1 = np.array((x1, y1))
    p2 = np.array((x2, y2))
    return np.linalg.norm(p1 - p2)


def GetPosition(initial_Coordinates, Coordinates, distances):
    result = minimize(
        mse,                         # The error function
        initial_Coordinates,            # The initial guess
        args=(Coordinates, distances),  # Additional parameters for mse
        method='L-BFGS-B',           # The optimisation algorithm
        options={
            'ftol': 1e-5,         # Tolerance
            'maxiter': 1e+7      # Maximum iterations
        })
    Coordinates = result.x
    return Coordinates
