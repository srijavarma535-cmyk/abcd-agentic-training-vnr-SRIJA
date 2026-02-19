def exponential_search(arr, target):
    if arr[0] == target:
        return 0

    i = 1
    while i < len(arr) and arr[i] <= target:
        i *= 2

    return exponential_search(arr[:min(i, len(arr))], target)

arr = [10, 20, 30, 40, 50]
print(exponential_search(arr, 30))
