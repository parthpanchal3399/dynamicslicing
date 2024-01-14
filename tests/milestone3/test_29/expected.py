def slice_me():
    x = 10
    l = [1, 2, 3, 4, 5]
    while len(l) > 0:
        print(l)
        m = l.pop()
        x -= m
        if x == 0:
            pass
        else:
            print(x)

    return x # slicing criterion

slice_me()