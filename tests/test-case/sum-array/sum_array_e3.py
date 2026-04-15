from functools import reduce
import operator

def sum_array(arr):
    return reduce(operator.add, arr, 0)
