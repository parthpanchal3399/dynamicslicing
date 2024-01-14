def slice_me():
    x = 10
    y = 2
    z = 3
    if x < y:
        pass
    elif x > z:
        z -= 5
        print(z)
    return z # slicing criterion

slice_me()