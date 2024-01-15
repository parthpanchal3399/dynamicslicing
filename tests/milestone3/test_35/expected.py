def slice_me():
    x = 10
    y = 20
    if not x == y:
        x = x + y
        y = 2 * y

    return x + y  # slicing criterion


slice_me()