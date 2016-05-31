from math import sqrt
import numpy as np


def custom_mean(s):
    """
    Mean that adapt to the amount of component available
    """
    res = []
    for i in range(max([len(vector) for vector in s])):
        res.append(np.mean([vector[i]
                            for vector in s
                            if len(vector) > i]))
    return res


def custom_std(s):
    """
    Std that adapt to the amount of component available
    """
    res = []
    for i in range(max([len(vector) for vector in s])):
        res.append(np.std([vector[i]
                           for vector in s
                           if len(vector) > i]))
    return res


def distance(x1, x2, y1, y2):
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
