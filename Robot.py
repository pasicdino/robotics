import math

from Sensor import Sensor


class Robot:

    def __init__(self, x, y, power):
        self.radius = 20
        self.x = x
        self.y = y
        self.power = power

        #indicating the motor speed values
        self.v_right = 0
        self.v_left = 0

        self.orientation = 0

        self.sensors = [0]*12
        for i in range(12):
            self.sensors[i] = Sensor(i*30, self)

        self.sensor_distances = [0]*12


    def right_motor(self, boolean, forward):
        if boolean:
            if forward:
                self.v_right = self.power
            else:
                self.v_right = -self.power
        else:
            self.v_right = 0

    def left_motor(self, boolean, forward):
        if boolean:
            if forward:
                self.v_left = self.power
            else:
                self.v_left = -self.power
        else:
            self.v_left = 0

    def update(self, dt): 
        R = self.radius
        L = 2 * R
        omega = (self.v_right - self.v_left) / L
        v = (self.v_right + self.v_left) / 2

        self.orientation += omega * dt
        #force orientation to be between 0 and 2pi
        self.orientation %= (2 * math.pi)

        self.x += v * dt * math.cos(self.orientation)
        self.y += v * dt * math.sin(self.orientation)


    def update_sensors(self, walls):
        for idx, sensor in enumerate(self.sensors):
            sensor.update_lines()   # update sensor line positions 
            sensor.check_intersect(walls)   # check for intersections with walls
            self.sensor_distances[idx] = sensor.distance    # add distance of sensor to distance array for ANN
