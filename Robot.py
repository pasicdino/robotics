import math
from shapely.geometry import LineString, Point

from Sensor import WallSensor, FeatureSensor

class Robot:

    def __init__(self, x, y, power, HEIGHT):
        self.radius = 20
        self.x = x
        self.y = y
        self.power = power

        #indicating the motor speed values
        self.v_right = 0
        self.v_left = 0

        self.direction = 0          #indicates direction of movement (1: forward/stationary, -1: backward)
        self.orientation = 0

        self.wall_sensors = [WallSensor(i * 30, self) for i in range(12)]
        self.wall_sensor_distances = [0]*12

        self.feature_sensor = FeatureSensor(200, self)
        self.detected_features = []         #holds detected features from omni-directional sensor, together with distance to robot - [[distance, bearing, feature]]

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
        for idx, sensor in enumerate(self.wall_sensors):
            sensor.update_lines()   #update sensor line positions
            sensor.check_intersect(walls)   #check for intersections with walls
            self.wall_sensor_distances[idx] = sensor.distance    #add distance of sensor to distance array for ANN

    def update_feature_sensors(self, map_walls, map_features):
        self.detected_features = self.feature_sensor.sense_features(map_walls, map_features)

    def is_collision(self):
        collision = any(x<=0 for x in self.wall_sensor_distances)
        return collision
    
    #Detects features within omni-sensor range and calculates distance + relative bearing
    def sense_features(self, map_features):
        self.detected_features = []
        for feature in map_features:
            exact_distance = Point(self.x, self.y).distance(feature.point)
            if exact_distance < self.feature_sensor_length:
                vector = (feature.x - self.x, feature.y - self.y)
                relative_bearing = math.degrees(math.atan2(vector[0], vector[1]) - self.orientation) % 360
                self.detected_features.append((feature, exact_distance, relative_bearing))


