def slice_me():
    x = 10
    d = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e'}
    for i in d:
        if i < x:
            d[i] = 'LESS'

    return d # slicing criterion

slice_me()