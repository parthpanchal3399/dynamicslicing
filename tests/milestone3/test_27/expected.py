def slice_me():
    x = 10
    for i in range(1, 6):
        if i > x:
            x += i
        else:
            x -= i

    return x # slicing criterion

slice_me()