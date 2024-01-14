def slice_me():
    first = [2, 4, 6]
    second = [2, 4, 6]
    result = []
    for i in first:
        for j in second:
            if i == j:
                pass
            else:
                s = str(i) + ' * ' + str(j) +  ' = ' + str(i * j)
                result.append(s)
        print("done with iteration", i)
    return result # slicing criterion

slice_me()