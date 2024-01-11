def slice_me():
    x = 10
    y = 2
    z = 3
    t = "world"
    if x > z or t == "hello":
        y += 2
    elif x == 5:
        z -= 5
    else:
        z = 0
    return y # slicing criterion

slice_me()