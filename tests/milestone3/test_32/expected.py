def slice_me():
    first = [2, 4, 6]
    second = [2, 4, 6]
    result = []
    while len(first) > 0:
        i = first[0]
        while len(second) > 0:
            j = second[0]
            if i == j:
                pass
            else:
                s = str(i) + ' * ' + str(j) +  ' = ' + str(i * j)
                result.append(s)
            second = second[1:]
        first = first[1:]
    return result # slicing criterion

slice_me()