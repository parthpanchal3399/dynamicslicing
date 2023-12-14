def Add(a, b):
    return a + b


def slice_me():
    x = 10
    y = 20
    h = "Hello"
    z = Add(x, y)
    k = "world"
    print(z)  # slicing criterion
    x += 10
    print(h, k)


slice_me()
