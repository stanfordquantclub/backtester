import numpy as np

def vel_list(list):
    vel_list = [0]
    for ind in range(len(list) - 1):
        vel_list.append((list[ind + 1] - list[ind]) / list[ind])

    return vel_list

def simple_momentum(list, period):
    simple_momentum = 0
    count = 1
    thelist = []

    while len(thelist) < period:
        if count >= len(list) + 1:
            return 0
        elif count < len(list) + 1:
            if count == 1:
                thelist.append(list[(-1) * count])
                count += 1
                continue
            elif count != 1:
                if list[(-1) * count + 1] !=  list[(-1) * count]:
                    thelist.append(list[(-1) * count])
                count += 1
        

    simple_momentum = sum(thelist)
    return simple_momentum/period

"""
Description: takes a list and returns the weighted sum of the list more recently elements get

Args:
    list: list of values
    period: how many elements should be considered in the calculation
    
Returns:
    [floats]: the sum of the list

"""
def weighted_momentum(list, period, grouping = 5):
    momentumvalue = 0
    count = 0
    thelist = []

    while len(thelist) < period:
        if count < len(list):
            if list[(-1) * count] != 0:
                thelist.append(list[(-1) * count])
            count += 1
        elif count >= len(list):
            return 0
    
    thelist.reverse()
    subList = [thelist[n:n+grouping] for n in range(0, len(thelist), grouping)]
    
    for i in range(1, len(subList)+1):
        momentumvalue = momentumvalue + i*sum(subList[i-1])

    return momentumvalue
