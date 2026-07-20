def sum_array(arr):
    total = 0
    for i in range(len(arr)):
        total += arr[i + 1]
    return total
