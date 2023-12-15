def slice_me():
    c1 = Car(150)
    c2 = Car(250)
    c1.maxSpeed = 200
    c1.accelerate(200)  # slicing criterion
    c2.maxSpeed = 200
    c2.accelerate(200)


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