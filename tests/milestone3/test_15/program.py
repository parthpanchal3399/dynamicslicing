def slice_me():
    x = 10
    y = 2
    z = 3
    t = "hello"
    if x == 5 :
        y += 2
    elif x > z and t == "hello":
        z -= 5
    else:
        z = 0
    return z # slicing criterion

slice_me()