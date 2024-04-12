class Sensor:
    def __init__(self, degrees, robot):
        self.degrees = degrees
        self.robot = robot
        self.length = 7
        self.distance = self.length-robot.radius
