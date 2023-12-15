def slice_me():
    x = [1, 2, 3, 4, 4, 4, 8, 9, 9]
    y = [5, 6, "test"]
    x.extend(y)
    x[0] = 20
    y[2] = "hi"
    c = x.count(4)
    print(c) # slicing criterion
    print(y)



slice_me()
