from functools import reduce

def sum_array(arr):
    total = reduce(lambda a, b: a + b, arr)
    return total
