def slice_me():
    x = 10
    z = 0
    for i in range(1, 6):
        if i > x:
            x += i
            z += 1
        else:
            x -= i
            z -= 1

    return x # slicing criterion

slice_me()