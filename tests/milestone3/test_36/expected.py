def slice_me():
    z = 30
    m = 40

    if z > m:
        pass
    else:
        z = z - m
        m = z / 2

    return z + m # slicing criterion


slice_me()