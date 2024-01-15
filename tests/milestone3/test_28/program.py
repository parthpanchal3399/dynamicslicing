def slice_me():
    x = 10
    z = 0
    d = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e'}
    for i in d:
        if i < x:
            print(d[i], "is less than x")
            d[i] = 'LESS'
        else:
            print(d[i], "is greater than x")
            d[i] = 'GREATER'

    return d # slicing criterion

slice_me()