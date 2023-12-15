def slice_me():
    c1 = Car(150)
    c2 = Car(250)
    x = 400
    c1.maxSpeed = 230
    c1.accelerate(c2.maxSpeed)  # slicing criterion
    c2.maxSpeed = 200
    c2.accelerate(200)


class Car:
    def __init__(self, maxSpeed):
        self.maxSpeed = maxSpeed
        self.speed = 0

    def accelerate(self, speedLimit):
        print("Accelerating...")
        self.speed += 10
        if self.speed > speedLimit:
            print("Stop!")


slice_me()