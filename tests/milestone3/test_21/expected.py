def slice_me():
    x = 10
    y = 2
    z = 3
    t = "hello"
    if x > y:
        if t=="world":
            pass
        elif t=="hello":
            z += 3
    return z # slicing criterion

slice_me()