def slice_me():
    x = 10
    y = 2
    z = 3
    t = "hello"
    if x > y:
        if t=="hello":
            y += 2
            z += 2
            print(z, y, x)
    return z # slicing criterion

slice_me()