def slice_me():
    x = 10
    y = 2
    z = 3
    t = "hello"
    if x < y:
        pass
    elif x > z:
        if t=="world":
            pass
        elif t=="hello":
            z -= 5
            print(z)
    return z # slicing criterion

slice_me()