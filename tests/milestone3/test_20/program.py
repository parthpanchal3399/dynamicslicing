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
    elif x < z:
        z -= 5
        y += 10
        print(z)
    else:
        z = 0
    return z # slicing criterion

slice_me()