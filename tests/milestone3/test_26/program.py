def slice_me():
    x = 10
    y = [1, 2, 3, 4, 5]
    z = 0
    for i in y:
        if i > x:
            x += i
            z += 1
        else:
            x -= i
            z -= 1

    return x # slicing criterion

slice_me()