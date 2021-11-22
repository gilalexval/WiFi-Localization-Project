import math


def distanceFromRSSI(RSSI, TxPower):
    # Calculate Distance from AP with the Formula
    #   Distance = 10^((MeasuredPower - RSSI)/(10*n))
    # Donde:
    # MeasuredPower -> RSSI a 1 m del AP
    # RSSI -> Leido por el dispositivo
    # n -> un factor entre 2 y 4 dependiente del nivel de interferencias que puede haber
    # mValue = -35 -> se puede reemplazar por TxPower en dBm
    n = 2
    if TxPower is not None:
        distance = math.pow(10, ((TxPower - RSSI)/(10 * n)))
        return distance
    return None
