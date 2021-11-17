import math


def distanceFromRSSI(RSSI, mValue):
    # Calculate Distance from AP with the Formula
    #   Distance = 10^((MeasuredPower - RSSI)/(10*n))
    # Donde:
    # MeasuredPower -> RSSI a 1 m del AP
    # RSSI -> Leido por el dispositivo
    # n -> un factor entre 2 y 4 dependiente del nivel de interferencias que puede haber
    # mValue = -35 -> se puede reemplazar por TxPower en dBm
    n = 2
    if mValue is not None:
        distance = math.pow(10, ((mValue - RSSI)/(10 * n)))
        return distance
    return None
