def slice_me():
    x = 10
    y = [1, 2, 3, 4, 5]
    for i in y:
        if i < x:
            x += i

    return x # slicing criterion

slice_me()