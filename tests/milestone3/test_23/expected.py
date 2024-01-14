def slice_me():
    x = 10
    y = 2
    z = 3
    t = "hello"
    if x < y:
        pass
    elif x > z:
        if t=="hello":
            y += 3
            z += 3
            print(z, y, x)
        z -= 5
        y += 10
        print(z)
    return z # slicing criterion

slice_me()