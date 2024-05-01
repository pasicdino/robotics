import math
from shapely.geometry import LineString, Point

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

        self.direction = 0          #indicates direction of movement (1: forward/stationary, -1: backward)
        self.orientation = 0

        self.sensors = [Sensor(i * 30, self) for i in range(12)]
        self.sensor_distances = [0]*12

        self.feature_sensor_length = 120
        self.detected_features = []         #holds detected features from omni-directional sensor, together with distance to robot - [tuple(feature, distance)]

        self.velocity_vector = (0, 0)

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

        #Update orientation
        self.orientation += omega * dt
        self.orientation %= (2 * math.pi)

        #Update direction (1: forward/stationary, -1: backward)
        self.direction = math.copysign(1, v)

        #Initial movement calculation
        dx = v * dt * math.cos(self.orientation)
        dy = v * dt * math.sin(self.orientation)
        proposed_x = self.x + dx
        proposed_y = self.y + dy

        #Used for initial collision check
        movement_line = LineString([(self.x, self.y), (proposed_x, proposed_y)]).buffer(R)

        #Detect initial collision, also decomposes the vector
        for wall in walls:
            if movement_line.intersects(wall.line):
                movement_vector = (self.direction * self.power * math.cos(self.orientation), self.direction * self.power * math.sin(self.orientation))
                dot_product = movement_vector[0] * wall.vector_normalized[0] + movement_vector[1] * \
                              wall.vector_normalized[1]
                parallel_component = (dot_product * wall.vector_normalized[0], dot_product * wall.vector_normalized[1])
                dx = parallel_component[0] * dt
                dy = parallel_component[1] * dt
                proposed_x = self.x + dx
                proposed_y = self.y + dy
                break

        #Recreate movement line using the parallel component only
        movement_line = LineString([(self.x, self.y), (proposed_x, proposed_y)]).buffer(R)

        #Secondary collision check to ensure that the parallel component will not lead to penetrating walls
        for wall in walls:
            if movement_line.intersects(wall.line):
                proposed_x = self.x
                proposed_y = self.y
                break

        self.x = proposed_x
        self.y = proposed_y
        self.velocity_vector = (dx / dt, dy / dt)

    def update_sensors(self, walls):
        for idx, sensor in enumerate(self.sensors):
            sensor.update_lines()   #update sensor line positions
            sensor.check_intersect(walls)   #check for intersections with walls
            self.sensor_distances[idx] = sensor.distance    #add distance of sensor to distance array for ANN

    def is_collision(self):
        collision = any(x<=0 for x in self.sensor_distances)
        return collision
    
    #Detects features within omni-sensor range
    def sense_features(self, map_features):
        self.detected_features = []
        for feature in map_features:
            distance = Point(self.x, self.y).distance(feature.point)
            if distance < self.feature_sensor_length:
                self.detected_features.append((feature, distance))
