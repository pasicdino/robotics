import math
from shapely.geometry import LineString, Point
from shapely.ops import nearest_points

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

        self.collision_margin = 0.001

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

    def update(self, dt, walls): 
        R = self.radius
        L = 2 * R
        omega = (self.v_right - self.v_left) / L
        v = (self.v_right + self.v_left) / 2

        self.orientation += omega * dt
        #force orientation to be between 0 and 2pi
        self.orientation %= (2 * math.pi)

        # COLLISION HANDLING
        # --- 
        collisions = self.check_collision(walls)
        if any(collisions):
            for idx, collision_point in enumerate(collisions):
                if collision_point:
                    
                    collision_vector = [collision_point.x - self.x, collision_point.y - self.y] # vector from robot center to collision point
                    collision_distance = math.sqrt(collision_vector[0]**2 + collision_vector[1]**2) # distance of collision vector
                    intersection_depth =  self.radius - collision_distance  # calculate how much the robot penetrated the wall

                    # move robot outside wall using intersection depth and a small margin
                    self.x -= (intersection_depth + self.collision_margin) * (collision_vector[0] / collision_distance)
                    self.y -= (intersection_depth + self.collision_margin) * (collision_vector[1] / collision_distance)
            return
        # ---
        
        # update robot coordinates 
        self.x = self.x + v * dt * math.cos(self.orientation)
        self.y = self.y + v * dt * math.sin(self.orientation)

    def check_collision(self, walls):
        intersection_points = [[]]*len(walls)
        robot_center = Point(self.x, self.y)
        robot_circle = robot_center.buffer(self.radius).boundary    # bounding object of robot

        for idx, wall in enumerate(walls):
            wall_line = LineString([(wall[0], wall[1]), (wall[2], wall[3])])    # LineString used for finding intersection
            if robot_circle.intersection(wall_line):
                intersection_points[idx] = list(nearest_points(robot_circle, wall_line))[0] # calculates point of intersection with wall and adds it to list

        return intersection_points

    def update_sensors(self, walls):
        for idx, sensor in enumerate(self.sensors):
            sensor.update_lines()   # update sensor line positions 
            sensor.check_intersect(walls)   # check for intersections with walls
            self.sensor_distances[idx] = sensor.distance    # add distance of sensor to distance array for ANN
