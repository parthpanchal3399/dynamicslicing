def slice_me():
    x = 10
    y = 20
    z = 30
    m = 40
    if x > y:
        x = x + y
        y = 2 * x
    else:
        x = x - y
        y = x / 2

    if z > m:
        z = z + m
        m = 2 * z
    else:
        z = z - m
        m = z / 2

    return z + m # slicing criterion


slice_me()