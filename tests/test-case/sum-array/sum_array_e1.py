from functools import reduce

def sum(arr):
    s = reduce(lambda a, b: a + b, arr)
    return s
