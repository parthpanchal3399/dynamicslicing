class Car:
    def __init__(self, name, topspeed):
        self.name = name
        self.topspeed = topspeed
        self.speed = 0

    def Accelerate(self, speed):
        self.speed += speed


def slice_me():
    c1 = Car("Mercedes", 200)
    c2 = Car("Porche", 250)
    while c1.speed < c1.topspeed:
        c1.Accelerate(50)
        c1.Accelerate(50)

    while c2.speed < c2.topspeed:
        c2.Accelerate(50)
        c2.Accelerate(50)

    if c1.speed > c2.speed:
        pass
    else:
        c2.name += " is faster"

    return c2  # slicing criterion


slice_me()