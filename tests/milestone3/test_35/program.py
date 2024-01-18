def slice_me():
    x = 10
    y = 20
    z = 30
    t = "hello"
    if not x == y:
        x = x + y
        y = 2 * y
        print(x, y, z)
    else:
        x = x - y
        y = 0
        print(x, y, z)

    return x + y  # slicing criterion


slice_me()