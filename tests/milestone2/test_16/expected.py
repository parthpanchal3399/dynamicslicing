def slice_me():
    c1 = Car(150)
    x = 400
    c1.maxSpeed = x
    c1.accelerate(x)  # slicing criterion


class Car:
    def __init__(self, maxSpeed):
        self.maxSpeed = maxSpeed
        self.speed = 0

    def accelerate(self, maxSpeed):
        print("Accelerating...")
        self.speed += 10
        if self.speed > self.maxSpeed:
            print("Stop!")


slice_me()