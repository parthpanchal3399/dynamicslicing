def slice_me():
    x = [1, 2, 3, 4]
    y = [5, 6, "test"]
    x.extend(y)
    x[0] = 20
    print(x) # slicing criterion



slice_me()
