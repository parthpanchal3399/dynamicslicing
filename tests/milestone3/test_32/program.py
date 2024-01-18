def slice_me():
    first = [2, 4, 6]
    second = [2, 4, 6]
    result = []
    t = "hello"
    while len(first) > 0:
        i = first[0]
        while len(second) > 0:
            j = second[0]
            if i == j:
                t += "world"
            else:
                s = str(i) + ' * ' + str(j) +  ' = ' + str(i * j)
                result.append(s)
            second = second[1:]
        print("done with iteration", i)
        first = first[1:]
    return result # slicing criterion

slice_me()