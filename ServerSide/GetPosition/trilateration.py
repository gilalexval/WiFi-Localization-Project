# Mean Square Error
# locations: [ (lat1, long1), ... ]
# distances: [ distance1, ... ]

import numpy as np
from scipy.optimize import minimize
import math


def mse(x, locations, distances):
    mse = 0.0
    for location, distance in zip(locations, distances):
        distance_calculated = euclidean_distance(
            x[0], x[1], location[0], location[1])
        mse += math.pow(distance_calculated - distance, 2.0)
    return mse / len(distances)


def euclidean_distance(x1, y1, x2, y2):
    p1 = np.array((x1, y1))
    p2 = np.array((x2, y2))
    return np.linalg.norm(p1 - p2)

#result = mse(x, locations, distances)
# print(result)
# initial_location: (lat, long)
# locations: [ (lat1, long1), ... ]
# distances: [ distance1,     ... ]


def GetPosition(initial_location, locations, distances):
    result = minimize(
        mse,                         # The error function
        initial_location,            # The initial guess
        args=(locations, distances),  # Additional parameters for mse
        method='L-BFGS-B',           # The optimisation algorithm
        options={
            'ftol': 1e-5,         # Tolerance
            'maxiter': 1e+7      # Maximum iterations
        })
    location = result.x
    print(location)
    return location
