def slice_me():
    x = 10
    y = 2
    z = 3
    t = "hello"
    if x < y:
        pass
    elif x > z:
        if t=="hello":
            z += 3
        z -= 5
    return z # slicing criterion

slice_me()