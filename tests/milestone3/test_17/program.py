def slice_me():
    x = 10
    y = 2
    z = 3
    t = "hello"
    if x > y and t=="hello":
        y += 2
        z += 2
        print(z)
    elif x < z:
        z -= 5
    else:
        z = 0
    return y # slicing criterion

slice_me()