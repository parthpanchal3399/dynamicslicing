def slice_me():
    x = 10
    z = 0
    l = [1, 2, 3, 4, 5]
    while len(l) > 0:
        print(l)
        m = l.pop()
        z += m
        x -= m
        if x == 0:
            z = 0
        else:
            print(x)

    return x # slicing criterion

slice_me()